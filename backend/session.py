"""Session memory management for conversation context."""

import json
import os
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field, asdict
from pathlib import Path


@dataclass
class Message:
    role: str  # "user" or "assistant"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: dict = field(default_factory=dict)


@dataclass
class Session:
    session_id: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    messages: list[Message] = field(default_factory=list)
    context: dict = field(default_factory=dict)  # For storing parsed hands, preferences, etc.
    
    def add_message(self, role: str, content: str, metadata: dict = None):
        """Add a message to the session."""
        msg = Message(role=role, content=content, metadata=metadata or {})
        self.messages.append(msg)
        return msg
    
    def get_conversation_history(self, max_messages: int = 20) -> list[dict]:
        """Get conversation history in format suitable for Claude."""
        recent = self.messages[-max_messages:] if len(self.messages) > max_messages else self.messages
        return [{"role": m.role, "content": m.content} for m in recent]
    
    def get_context_summary(self) -> str:
        """Get a summary of session context for the LLM."""
        if not self.context:
            return ""

        parts = []

        if "current_hand" in self.context:
            parts.append(f"Current hand being analyzed: {self.context['current_hand']}")

        if "last_hole_cards" in self.context:
            parts.append(f"Last solved hole cards (13 cards): {self.context['last_hole_cards']}")

        if "last_solution" in self.context:
            parts.append(f"Last solver solution (Top-Middle-Bottom): {self.context['last_solution']}")

        if "last_ev" in self.context:
            parts.append(f"Last solution EV: {self.context['last_ev']}")

        if "last_alternatives" in self.context:
            alts = self.context["last_alternatives"]
            if alts:
                alt_strs = [f"  - {a['solution']} (EV: {a.get('ev', '?')})" for a in alts[:3]]
                parts.append(f"Alternative solutions:\n" + "\n".join(alt_strs))

        if "dead_cards" in self.context:
            parts.append(f"Dead cards: {self.context['dead_cards']}")

        if "game_version" in self.context:
            parts.append(f"Game version: {self.context['game_version']}")

        if "recent_solutions" in self.context:
            parts.append(f"Recently viewed solutions: {len(self.context['recent_solutions'])} solutions")

        return "\n".join(parts)
    
    def set_context(self, key: str, value):
        """Set a context value."""
        self.context[key] = value
    
    def get_context(self, key: str, default=None):
        """Get a context value."""
        return self.context.get(key, default)
    
    def clear_context(self):
        """Clear all context."""
        self.context = {}


class SessionManager:
    """Manages multiple sessions with optional persistence."""
    
    def __init__(self, storage_dir: Optional[str] = None):
        self.sessions: dict[str, Session] = {}
        self.storage_dir = Path(storage_dir) if storage_dir else None
        
        if self.storage_dir:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def create_session(self, session_id: str = None) -> Session:
        """Create a new session."""
        if session_id is None:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        session = Session(session_id=session_id)
        self.sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get an existing session."""
        # Try memory first
        if session_id in self.sessions:
            return self.sessions[session_id]
        
        # Try loading from disk
        if self.storage_dir:
            session = self._load_session(session_id)
            if session:
                self.sessions[session_id] = session
                return session
        
        return None
    
    def get_or_create_session(self, session_id: str) -> Session:
        """Get existing session or create new one."""
        session = self.get_session(session_id)
        if session is None:
            session = self.create_session(session_id)
        return session
    
    def save_session(self, session: Session):
        """Save session to disk."""
        if not self.storage_dir:
            return
        
        filepath = self.storage_dir / f"{session.session_id}.json"
        
        # Convert to serializable format
        data = {
            "session_id": session.session_id,
            "created_at": session.created_at,
            "messages": [asdict(m) for m in session.messages],
            "context": session.context
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _load_session(self, session_id: str) -> Optional[Session]:
        """Load session from disk."""
        if not self.storage_dir:
            return None
        
        filepath = self.storage_dir / f"{session_id}.json"
        if not filepath.exists():
            return None
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            session = Session(
                session_id=data["session_id"],
                created_at=data.get("created_at", ""),
                context=data.get("context", {})
            )
            
            for msg_data in data.get("messages", []):
                session.messages.append(Message(**msg_data))
            
            return session
        except Exception as e:
            print(f"Error loading session {session_id}: {e}")
            return None
    
    def list_sessions(self) -> list[str]:
        """List all available session IDs."""
        session_ids = set(self.sessions.keys())
        
        if self.storage_dir:
            for filepath in self.storage_dir.glob("*.json"):
                session_ids.add(filepath.stem)
        
        return sorted(session_ids)
    
    def delete_session(self, session_id: str):
        """Delete a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
        
        if self.storage_dir:
            filepath = self.storage_dir / f"{session_id}.json"
            if filepath.exists():
                filepath.unlink()


# Default session manager with persistence
default_storage = os.path.join(os.path.dirname(__file__), '..', 'sessions')
session_manager = SessionManager(storage_dir=default_storage)
