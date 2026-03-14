"""Agent that uses Claude to answer OFC poker questions with real-time solving."""

import os
import json
from typing import Generator, Optional
from anthropic import Anthropic
from db import db
from prompts import SYSTEM_PROMPT, get_tool_definitions
from hand_parser import parse_ofc_hand, parse_cards, parse_any_cards, detect_hand_type
from visualizer import render_solution, render_cards_inline
from session import Session, session_manager

# Try to import solver (may not be available in all environments)
try:
    from solver import solve_hand, get_solver, GAME_VERSIONS
    SOLVER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Solver not available in agent.py: {e}")
    SOLVER_AVAILABLE = False
    solve_hand = None
    get_solver = None
    GAME_VERSIONS = {}
from strategy import (
    get_pattern_advice, 
    identify_pattern, 
    get_all_patterns,
    get_strategic_principles,
    get_royalty_table,
    format_pattern_advice,
    format_all_patterns
)
from hand_validator import validate_solution_string


class OFCAgent:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.model = "claude-sonnet-4-20250514"
        self.max_tool_calls = 30
        
        # Warm up the solver on init (if available)
        if SOLVER_AVAILABLE:
            print("Initializing OFC solver...")
            get_solver()
            print("Solver ready.")
        else:
            print("Solver not available - running in query-only mode.")
    
    def process_tool_call(self, tool_name: str, tool_input: dict, session: Optional[Session] = None) -> str:
        """Execute a tool and return the result as a string."""
        
        if tool_name == "get_strategy":
            # STRATEGIC PATTERN ADVICE TOOL
            query = tool_input.get("query", "").strip()
            
            print(f"  📚 Strategy query: {query}")
            
            # Handle special queries
            if query.lower() == "all":
                patterns = get_all_patterns()
                return json.dumps({
                    "success": True,
                    "type": "all_patterns",
                    "patterns": {k: {
                        "pattern": v.pattern,
                        "distribution": v.distribution,
                        "reasoning": v.reasoning,
                        "examples": v.examples,
                        "royalty_potential": v.royalty_potential,
                        "foul_risk": v.foul_risk
                    } for k, v in patterns.items()},
                    "count": len(patterns)
                })
            
            elif query.lower() == "principles":
                principles = get_strategic_principles()
                return json.dumps({
                    "success": True,
                    "type": "principles",
                    "principles": principles
                })
            
            elif query.lower() == "royalties":
                royalties = get_royalty_table()
                return json.dumps({
                    "success": True,
                    "type": "royalties",
                    "royalties": royalties
                })
            
            # Try to identify pattern from natural language
            pattern_key = identify_pattern(query)
            
            if not pattern_key:
                # Try direct pattern key lookup
                pattern_key = query.lower().replace(" ", "_")
            
            advice = get_pattern_advice(pattern_key)
            
            if advice:
                print(f"  ✅ Found pattern: {advice.pattern}")
                return json.dumps({
                    "success": True,
                    "type": "pattern_advice",
                    "pattern": advice.pattern,
                    "distribution": advice.distribution,
                    "reasoning": advice.reasoning,
                    "examples": advice.examples,
                    "royalty_potential": advice.royalty_potential,
                    "foul_risk": advice.foul_risk,
                    "formatted": format_pattern_advice(advice)
                })
            else:
                print(f"  ❌ Pattern not found: {query}")
                available_patterns = list(get_all_patterns().keys())
                return json.dumps({
                    "success": False,
                    "error": f"Pattern not found: {query}",
                    "available_patterns": available_patterns,
                    "hint": "Try: 'all' to see all patterns, or provide a pattern like '5_pairs_3_singles'"
                })
        
        elif tool_name == "solve_hand":
            # PRIMARY TOOL: Real-time CFR solving
            if not SOLVER_AVAILABLE:
                return json.dumps({
                    "success": False,
                    "error": "Solver not available in this environment. The C++ framework module is required for GTO solving."
                })
            
            hole_cards = tool_input.get("hole_cards", "")
            dead_cards = tool_input.get("dead_cards", "")
            game_version = tool_input.get("game_version", 2)
            # Use Railway Pro config defaults (1000×10)
            from solver import DEFAULT_ITERATIONS, DEFAULT_TRAVERSALS
            iterations = tool_input.get("iterations", DEFAULT_ITERATIONS)
            traversals = tool_input.get("traversals", DEFAULT_TRAVERSALS)
            
            print(f"  🎯 Solving: {hole_cards[:30]}... (v{game_version}, {iterations} iters)")
            
            try:
                result = solve_hand(
                    hole_cards=hole_cards,
                    dead_cards=dead_cards,
                    game_version=game_version,
                    iterations=iterations,
                    traversals=traversals
                )
                
                # CRITICAL: Validate solution structure
                is_valid, error = validate_solution_string(result.solution)

                # Format result for LLM
                response = {
                    "success": True,
                    "IMPORTANT": "You MUST present this exact solution to the user. Do NOT substitute your own arrangement.",
                    "solution": result.solution,
                    "ev": result.ev,
                    "frequency_percent": result.frequency,
                    "alternatives": result.alternatives,
                    "game": GAME_VERSIONS.get(game_version, {}).get("name", f"Version {game_version}"),
                    "computation": {
                        "iterations": iterations,
                        "traversals": traversals
                    },
                    "is_valid": is_valid
                }

                # Add foul warning if invalid
                if not is_valid:
                    response["foul_error"] = error
                    response["warning"] = "⚠️ This solution appears to FOUL. Do not use!"
                    print(f"  ⚠️ FOUL DETECTED: {error}")

                print(f"  ✅ Solution: {result.solution} (EV: {result.ev})")

                # Store in session context for follow-up questions
                if session:
                    session.set_context("last_solution", result.solution)
                    session.set_context("last_hole_cards", hole_cards)
                    session.set_context("last_ev", result.ev)
                    session.set_context("last_alternatives", result.alternatives[:5] if result.alternatives else [])

                return json.dumps(response)
                
            except Exception as e:
                print(f"  ❌ Solver error: {e}")
                return json.dumps({
                    "success": False,
                    "error": str(e),
                    "hint": "Check card format: 13 hole cards + appropriate dead cards for game version"
                })
        
        elif tool_name == "execute_sql":
            # SECONDARY TOOL: Database queries for patterns
            query = tool_input.get("query", "")
            reasoning = tool_input.get("reasoning", "")
            
            if not query.strip().upper().startswith("SELECT"):
                return json.dumps({
                    "success": False,
                    "error": "Only SELECT queries are allowed."
                })
            
            print(f"  📊 SQL: {query[:80]}...")
            result = db.execute_query(query)
            
            if result.get("success"):
                if "columns" in result:
                    if result["row_count"] <= 10:
                        formatted_rows = []
                        for row in result["rows"]:
                            formatted_row = {col: val for col, val in zip(result["columns"], row)}
                            formatted_rows.append(formatted_row)
                        result["formatted"] = formatted_rows
                    else:
                        result["note"] = f"Large result ({result['row_count']} rows). Focus on patterns."
                    
                    print(f"  ✅ Got {result['row_count']} rows")
            else:
                print(f"  ❌ Query failed: {result.get('error')}")
            
            return json.dumps(result, default=str)
        
        elif tool_name == "parse_hand":
            hand_input = tool_input.get("hand_input", "")
            input_type = tool_input.get("input_type", "cards")
            
            print(f"  🎴 Parsing: {hand_input[:50]}...")
            
            result = {"success": False}
            
            if input_type == "full_hand":
                hand = parse_ofc_hand(hand_input)
                if hand:
                    result = {
                        "success": True,
                        "solution_format": hand.to_solution_format(),
                        "top": {
                            "cards": [str(c) for c in hand.top],
                            "display": render_cards_inline(hand.top, use_colors=False),
                            "hand_type": detect_hand_type(hand.top)
                        },
                        "middle": {
                            "cards": [str(c) for c in hand.middle],
                            "display": render_cards_inline(hand.middle, use_colors=False),
                            "hand_type": detect_hand_type(hand.middle)
                        },
                        "bottom": {
                            "cards": [str(c) for c in hand.bottom],
                            "display": render_cards_inline(hand.bottom, use_colors=False),
                            "hand_type": detect_hand_type(hand.bottom)
                        }
                    }
                    if session:
                        session.set_context("current_hand", hand.to_solution_format())
                else:
                    result["error"] = "Could not parse as full OFC hand"
            else:
                cards = parse_cards(hand_input)
                if not cards:
                    cards = parse_any_cards(hand_input)
                
                if cards:
                    result = {
                        "success": True,
                        "cards": [str(c) for c in cards],
                        "cards_string": " ".join(str(c) for c in cards),
                        "display": render_cards_inline(cards, use_colors=False),
                        "count": len(cards),
                        "hand_type": detect_hand_type(cards) if len(cards) in [3, 5] else None
                    }
                    if session:
                        session.set_context("current_cards", [str(c) for c in cards])
                else:
                    result["error"] = f"Could not parse cards from: {hand_input}"
            
            return json.dumps(result)
        
        elif tool_name == "visualize_solution":
            solution = tool_input.get("solution", "")
            print(f"  🖼️ Visualizing: {solution[:50]}...")
            
            try:
                viz = render_solution(solution, use_colors=False)
                return json.dumps({
                    "success": True,
                    "visualization": viz,
                    "note": "Show this in a code block"
                })
            except Exception as e:
                return json.dumps({
                    "success": False,
                    "error": str(e)
                })
        
        elif tool_name == "set_context":
            key = tool_input.get("key", "")
            value = tool_input.get("value", "")
            
            if session:
                session.set_context(key, value)
                return json.dumps({"success": True, "stored": {key: value}})
            return json.dumps({"success": False, "error": "No active session"})
        
        elif tool_name == "get_context":
            key = tool_input.get("key", "")
            
            if session:
                value = session.get_context(key)
                if value is not None:
                    return json.dumps({"success": True, "key": key, "value": value})
                return json.dumps({"success": False, "error": f"No context for: {key}"})
            return json.dumps({"success": False, "error": "No active session"})
        
        return json.dumps({"error": f"Unknown tool: {tool_name}"})
    
    def chat(self, user_message: str, session: Optional[Session] = None, 
             conversation_history: list = None) -> str:
        """Process a user message and return the agent's response."""
        
        if session:
            messages = session.get_conversation_history()
            messages.append({"role": "user", "content": user_message})
            
            context_summary = session.get_context_summary()
            system = SYSTEM_PROMPT
            if context_summary:
                system += f"\n\n## Current Session Context\n{context_summary}"
        elif conversation_history:
            messages = conversation_history + [{"role": "user", "content": user_message}]
            system = SYSTEM_PROMPT
        else:
            messages = [{"role": "user", "content": user_message}]
            system = SYSTEM_PROMPT
        
        tool_call_count = 0
        
        while tool_call_count < self.max_tool_calls:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system,
                tools=get_tool_definitions(),
                messages=messages
            )
            
            if response.stop_reason == "tool_use":
                tool_uses = [block for block in response.content if block.type == "tool_use"]
                messages.append({"role": "assistant", "content": response.content})
                
                tool_results = []
                for tool_use in tool_uses:
                    result = self.process_tool_call(tool_use.name, tool_use.input, session)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": result
                    })
                    tool_call_count += 1
                
                messages.append({"role": "user", "content": tool_results})
                
            else:
                text_blocks = [block.text for block in response.content if hasattr(block, 'text')]
                final_response = "\n".join(text_blocks)
                
                if session:
                    session.add_message("user", user_message)
                    session.add_message("assistant", final_response)
                    session_manager.save_session(session)
                
                return final_response
        
        return "I've reached the maximum number of operations. Please try a simpler question."
    
    def chat_stream(self, user_message: str, session: Optional[Session] = None) -> Generator[str, None, None]:
        """Stream the agent's response."""
        response = self.chat(user_message, session)
        yield response


# Singleton instance
agent = OFCAgent()
