"""FastAPI backend for OFC Solver AI."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from agent import agent
from db import db
from session import session_manager
from hand_parser import parse_ofc_hand, parse_cards, detect_hand_type
from visualizer import render_solution, render_ofc_hand_html, get_card_css

# Try to import solver (may not be available in all environments)
try:
    from solver import OFCSolver
    SOLVER_AVAILABLE = True
    print("✅ Solver module loaded successfully")
except ImportError as e:
    print(f"❌ Solver not available: {e}")
    SOLVER_AVAILABLE = False
    OFCSolver = None
    
    # Try to import framework directly to diagnose
    try:
        import framework
        print("✅ Framework module found but solver.py has issues")
    except ImportError as e2:
        print(f"❌ Framework module not found: {e2}")

from auth import (
    authenticate_user, create_access_token, verify_token, 
    get_user, list_users, create_user
)

app = FastAPI(
    title="OFC Solver AI",
    description="AI-powered Open-Face Chinese Poker analysis using GTO solutions",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)


# Auth dependency - checks both Authorization and X-App-Auth headers
# X-App-Auth is used when Authorization carries tunnel basic auth
async def get_current_user(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token and return current user."""
    token = None
    
    # First check X-App-Auth header (used when tunnel basic auth is in Authorization)
    x_app_auth = request.headers.get("x-app-auth", "")
    if x_app_auth.startswith("Bearer "):
        token = x_app_auth[7:]
    elif credentials:
        token = credentials.credentials
    
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    username = verify_token(token)
    
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user = get_user(username)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    
    return user


# Optional auth (for endpoints that work with or without auth)
async def get_optional_user(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user if authenticated, None otherwise."""
    token = None
    
    x_app_auth = request.headers.get("x-app-auth", "")
    if x_app_auth.startswith("Bearer "):
        token = x_app_auth[7:]
    elif credentials:
        token = credentials.credentials
    
    if not token:
        return None
    
    username = verify_token(token)
    
    if not username:
        return None
    
    return get_user(username)


# Request/Response models
class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    display_name: str


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    

class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    success: bool
    columns: Optional[list] = None
    rows: Optional[list] = None
    row_count: Optional[int] = None
    truncated: Optional[bool] = None
    error: Optional[str] = None


class ParseHandRequest(BaseModel):
    hand: str


class VisualizeRequest(BaseModel):
    solution: str
    format: Optional[str] = "ascii"


class SolveRequest(BaseModel):
    cards: str  # Space-separated card string (e.g., "Ah Kd Qc ...")
    game_version: Optional[int] = 2
    iterations: Optional[int] = 1000  # Railway Pro config (upgrade to 10000+ locally if needed)
    traversals: Optional[int] = 10    # Railway Pro config (upgrade to 100+ locally if needed)


# ============== Public Endpoints ==============

@app.get("/")
async def root():
    """Redirect to the app."""
    return RedirectResponse(url="/app")


@app.get("/health")
async def health():
    """Detailed health check including database."""
    try:
        result = db.execute_query("SELECT 1")
        db_status = "connected" if result.get("success") else "error"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "ok",
        "database": db_status
    }


@app.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Authenticate and get access token."""
    user = authenticate_user(request.username, request.password)
    
    if not user:
        raise HTTPException(
            status_code=401, 
            detail="Invalid username or password"
        )
    
    access_token = create_access_token(user.username)
    
    return LoginResponse(
        access_token=access_token,
        username=user.username,
        display_name=user.display_name or user.username
    )


@app.get("/auth/me")
async def get_me(user = Depends(get_current_user)):
    """Get current user info."""
    return {
        "username": user.username,
        "display_name": user.display_name,
        "is_active": user.is_active
    }


# ============== Protected Endpoints ==============

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, user = Depends(get_current_user)):
    """
    Chat with the OFC AI agent.
    
    Send a message and get an AI-powered response that can query
    the database to answer questions about GTO poker strategy.
    """
    try:
        # Get or create session (prefix with username for isolation)
        session_id = request.session_id or f"{user.username}_default"
        if not session_id.startswith(f"{user.username}_"):
            session_id = f"{user.username}_{session_id}"
        
        session = session_manager.get_or_create_session(session_id)
        
        response = agent.chat(request.message, session=session)
        
        return ChatResponse(
            response=response,
            session_id=session.session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest, user = Depends(get_current_user)):
    """Execute a raw SQL query (SELECT only)."""
    if not request.query.strip().upper().startswith("SELECT"):
        raise HTTPException(status_code=400, detail="Only SELECT queries are allowed")
    
    result = db.execute_query(request.query)
    return QueryResponse(**result)


@app.post("/parse")
async def parse_hand(request: ParseHandRequest, user = Depends(get_current_user)):
    """Parse an OFC hand and return structured data."""
    hand = parse_ofc_hand(request.hand)
    
    if hand:
        return {
            "success": True,
            "solution_format": hand.to_solution_format(),
            "top": {
                "cards": [str(c) for c in hand.top],
                "hand_type": detect_hand_type(hand.top)
            },
            "middle": {
                "cards": [str(c) for c in hand.middle],
                "hand_type": detect_hand_type(hand.middle)
            },
            "bottom": {
                "cards": [str(c) for c in hand.bottom],
                "hand_type": detect_hand_type(hand.bottom)
            }
        }
    
    cards = parse_cards(request.hand)
    if cards:
        return {
            "success": True,
            "cards": [str(c) for c in cards],
            "count": len(cards),
            "hand_type": detect_hand_type(cards) if len(cards) in [3, 5] else None
        }
    
    return {"success": False, "error": "Could not parse hand"}


@app.post("/visualize")
async def visualize(request: VisualizeRequest, user = Depends(get_current_user)):
    """Generate a visualization of an OFC solution."""
    hand = parse_ofc_hand(request.solution)
    
    if not hand:
        raise HTTPException(status_code=400, detail="Could not parse solution")
    
    if request.format == "html":
        return {
            "success": True,
            "html": render_ofc_hand_html(hand),
            "css": get_card_css()
        }
    else:
        return {
            "success": True,
            "ascii": render_solution(request.solution, use_colors=False)
        }


@app.post("/solve")
async def solve(request: SolveRequest, user = Depends(get_current_user)):
    """Solve an OFC hand using the GTO solver."""
    if not SOLVER_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="Solver not available in this environment. The C++ framework module is required."
        )
    
    print(f"\n{'='*60}")
    print(f"SOLVE REQUEST from {user.username}")
    print(f"Cards: {request.cards}")
    print(f"{'='*60}\n")
    
    try:
        from solver import GAME_VERSIONS
        from poker.ofc.utils import generate_deck
        import random
        from pathlib import Path
        
        # Check if lookup table exists
        lookup_dir = Path(__file__).parent / "lookup"
        lookup_file = lookup_dir / "13-ranks-4-duplicate-suits-with-jokers.dat"
        
        if lookup_file.exists():
            file_size = lookup_file.stat().st_size
            print(f"✅ Lookup table found: {lookup_file} ({file_size:,} bytes)")
        else:
            print(f"⚠️  Lookup table NOT found at: {lookup_file}")
            print(f"   Lookup dir contents: {list(lookup_dir.glob('*')) if lookup_dir.exists() else 'DIR NOT FOUND'}")
        
        print(f"Solving with cards: {request.cards}")
        
        # Initialize solver
        solver = OFCSolver()
        
        # Clean the cards string - solver expects format like "AhKdQc*2s..." where * is joker
        # Input from frontend: "Ah Kd Qc * 2s ..."
        # We need to keep spaces around jokers so they don't merge with adjacent cards
        cards_list = request.cards.split()
        cards_cleaned = "".join(cards_list)  # Join without spaces, jokers are single char
        
        print(f"Cards list: {cards_list}")
        print(f"Cards cleaned: {cards_cleaned}")
        
        # Get game config to see how many dead cards we need
        game = GAME_VERSIONS.get(request.game_version, GAME_VERSIONS[2])
        num_dead_cards = game["dead"]
        
        # Generate random dead cards if needed
        dead_cards = ""
        if num_dead_cards > 0:
            # Parse the selected cards
            from poker.parsing import parse_hand
            from poker.constants import CARD_JOKER
            selected = parse_hand(cards_cleaned)
            
            # Generate all cards: 52 regular cards + 1 joker (can be used multiple times)
            # Card indices: 0-51 (regular cards), 52 (joker)
            all_cards = list(range(53))  # 0-52 inclusive
            available = [c for c in all_cards if c not in selected]
            
            # Random sample for dead cards (with replacement if we have multiple jokers)
            if num_dead_cards <= len(available):
                dead_indices = random.sample(available, num_dead_cards)
            else:
                # Not enough cards available - shouldn't happen with 13 selected from 53 total
                raise ValueError(f"Not enough cards available for dead cards: need {num_dead_cards}, have {len(available)}")
            
            # Convert to string
            from solver import cards_to_string
            dead_cards = cards_to_string(dead_indices)
            print(f"Generated dead cards: {dead_cards}")
        
        # Solve the hand
        print(f"Calling solver with hole_cards={cards_cleaned}, dead_cards={dead_cards}")
        print(f"Creating solver instance...")
        
        import signal
        import sys
        
        # Add timeout to prevent hanging
        def timeout_handler(signum, frame):
            raise TimeoutError("Solver timed out after 60 seconds")
        
        # Set signal handler (Unix only)
        if hasattr(signal, 'SIGALRM'):
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(60)  # 60 second timeout
        
        try:
            print(f"About to call solver.solve() with:")
            print(f"  - iterations: {request.iterations}")
            print(f"  - traversals: {request.traversals}")
            print(f"  - game_version: {request.game_version}")
            print(f"Starting CFR computation...")
            
            result = solver.solve(
                hole_cards=cards_cleaned,
                dead_cards=dead_cards,
                game_version=request.game_version,
                iterations=request.iterations,
                traversals=request.traversals,
                top_n=5
            )
            
            print(f"CFR computation completed!")
            
            # Cancel alarm if it succeeded
            if hasattr(signal, 'SIGALRM'):
                signal.alarm(0)
            
            print(f"Solver returned: {result.solution}")
            
        except TimeoutError as e:
            if hasattr(signal, 'SIGALRM'):
                signal.alarm(0)
            print(f"❌ Solver timed out after 60 seconds!")
            print(f"   Try reducing iterations/traversals or run locally for better performance")
            raise HTTPException(
                status_code=504, 
                detail="Solver timed out (60s). Try reducing iterations or run the solver locally for better performance."
            )
        except Exception as e:
            if hasattr(signal, 'SIGALRM'):
                signal.alarm(0)
            print(f"❌ Solver crashed: {type(e).__name__}: {e}")
            raise
        
        # Ensure all data is JSON-serializable
        # Keep alternatives list small to avoid large responses
        alternatives = []
        if result.alternatives:
            for alt in result.alternatives[:3]:  # Limit to top 3 alternatives
                try:
                    alternatives.append({
                        "solution": str(alt.get("solution", "")),
                        "ev": float(alt.get("ev", 0.0)),
                        "frequency": float(alt.get("frequency", 0.0)),
                        "top": {
                            "cards": str(alt.get("top", {}).get("cards", "")),
                            "hand_type": str(alt.get("top", {}).get("hand_type", "Unknown"))
                        },
                        "middle": {
                            "cards": str(alt.get("middle", {}).get("cards", "")),
                            "hand_type": str(alt.get("middle", {}).get("hand_type", "Unknown"))
                        },
                        "bottom": {
                            "cards": str(alt.get("bottom", {}).get("cards", "")),
                            "hand_type": str(alt.get("bottom", {}).get("hand_type", "Unknown"))
                        }
                    })
                except Exception as e:
                    print(f"⚠️  Failed to serialize alternative: {e}")
        
        response_data = {
            "success": True,
            "solution": str(result.solution),
            "ev": float(result.ev) if result.ev is not None else 0.0,
            "frequency": float(result.frequency) if result.frequency is not None else 0.0,
            "alternatives": alternatives,
            "hole_cards": str(result.hole_cards),
            "dead_cards": str(result.dead_cards),
            "game_version": int(result.game_version),
            "iterations": int(result.iterations),
            "traversals": int(result.traversals)
        }
        
        print(f"✅ Response prepared: {len(str(response_data))} bytes")
        print(f"   Solution: {response_data['solution']}")
        print(f"   EV: {response_data['ev']}")
        print(f"   Alternatives: {len(response_data['alternatives'])}")
        print(f"{'='*60}\n")
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"\n{'!'*60}")
        print(f"❌ SOLVER ERROR:")
        print(error_details)
        print(f"{'!'*60}\n")
        raise HTTPException(status_code=500, detail=f"Solver error: {str(e)}")


@app.get("/schema")
async def schema(user = Depends(get_current_user)):
    """Get the database schema summary."""
    try:
        schema_text = db.get_schema_summary()
        return {"schema": schema_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def stats(user = Depends(get_current_user)):
    """Get database statistics."""
    stats = {}
    
    tables = ['solutions', 'alternative_solutions', 'spots', 'games', 'scores', 'queue']
    for table in tables:
        result = db.execute_query(f"SELECT COUNT(*) as count FROM {table}")
        if result.get("success") and result.get("rows"):
            stats[table] = result["rows"][0][0]
    
    return {"table_counts": stats}


@app.get("/sessions")
async def list_user_sessions(user = Depends(get_current_user)):
    """List sessions for current user."""
    all_sessions = session_manager.list_sessions()
    user_sessions = [s for s in all_sessions if s.startswith(f"{user.username}_")]
    return {"sessions": user_sessions}


@app.get("/sessions/{session_id}")
async def get_session(session_id: str, user = Depends(get_current_user)):
    """Get session details including conversation history."""
    # Ensure user can only access their own sessions
    if not session_id.startswith(f"{user.username}_"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session.session_id,
        "created_at": session.created_at,
        "message_count": len(session.messages),
        "context": session.context,
        "messages": [
            {"role": m.role, "content": m.content, "timestamp": m.timestamp}
            for m in session.messages
        ]
    }


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str, user = Depends(get_current_user)):
    """Delete a session."""
    if not session_id.startswith(f"{user.username}_"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    session_manager.delete_session(session_id)
    return {"success": True, "deleted": session_id}


# ============== Static Files (Frontend) ==============

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

@app.get("/app", response_class=HTMLResponse)
@app.get("/app/", response_class=HTMLResponse)
@app.get("/v3", response_class=HTMLResponse)
@app.get("/v3/", response_class=HTMLResponse)
@app.get("/v4", response_class=HTMLResponse)
@app.get("/v4/", response_class=HTMLResponse)
async def serve_app():
    """Serve the frontend app with inlined CSS and JS to avoid caching issues."""
    index_path = FRONTEND_DIR / "index.html"
    css_path = FRONTEND_DIR / "styles.css"
    js_path = FRONTEND_DIR / "app.js"
    
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Frontend not found")
    
    html = index_path.read_text()
    
    # Inline CSS and JS to avoid browser caching issues with tunnel auth
    if css_path.exists():
        css_content = css_path.read_text()
        html = html.replace(
            '<link rel="stylesheet" href="/static/styles.css">',
            f'<style>{css_content}</style>'
        )
    
    if js_path.exists():
        js_content = js_path.read_text()
        html = html.replace(
            '<script src="/static/app.js?v=2"></script>',
            f'<script>{js_content}</script>'
        )
        # Also handle without cache bust param
        html = html.replace(
            '<script src="/static/app.js"></script>',
            f'<script>{js_content}</script>'
        )
    
    from starlette.responses import Response
    return Response(
        content=html,
        media_type="text/html",
        headers={"Cache-Control": "no-cache, no-store, must-revalidate", "Pragma": "no-cache"}
    )

# Serve static files (CSS, JS)
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
