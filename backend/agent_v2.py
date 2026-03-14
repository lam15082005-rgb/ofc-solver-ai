"""Improved OFC Agent with tool chaining and dynamic context injection - v2."""

import os
import json
import re
from typing import Generator, Optional, List, Dict
from anthropic import Anthropic
from db import db
from prompts_v2 import build_dynamic_prompt, get_tool_definitions
from hand_parser import parse_ofc_hand, parse_cards, parse_any_cards, detect_hand_type
from visualizer import render_solution, render_cards_inline
from session import Session, session_manager

# Try to import solver (may not be available in all environments)
try:
    from solver import solve_hand, get_solver, GAME_VERSIONS
    SOLVER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Solver not available in agent_v2.py: {e}")
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
)
from hand_validator import validate_solution_string, add_foul_warning, format_hand_strength_comparison


class ImprovedOFCAgent:
    """Improved agent with smart tool selection and context injection."""
    
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.model = "claude-sonnet-4-20250514"
        self.max_tool_calls = 30
        
        # Warm up solver (if available)
        if SOLVER_AVAILABLE:
            print("Initializing OFC solver...")
            get_solver()
            print("Solver ready.")
        else:
            print("Solver not available - running in query-only mode.")
    
    def _detect_query_type(self, user_message: str) -> Dict[str, any]:
        """Analyze user message to determine intent and guide tool selection."""
        
        msg_lower = user_message.lower()
        
        # Check for exact 13 cards (cards are like "Ah", "Kd", etc.)
        card_pattern = r'\b([AKQJT2-9]\*?[hdcs]|\*[AKQJT2-9]?[hdcs]?)\b'
        cards_found = re.findall(card_pattern, user_message, re.IGNORECASE)
        has_13_cards = len(cards_found) >= 13
        
        # Check for pattern keywords
        pattern_keywords = ["pairs", "trips", "straight", "flush", "singles", "three of a kind"]
        has_pattern_query = any(kw in msg_lower for kw in pattern_keywords)
        
        # Check for statistical/analysis keywords (check BEFORE pattern keywords)
        analysis_keywords = ["average", "common", "most", "how many", "distribution", "statistics", "average ev"]
        has_analysis_query = any(kw in msg_lower for kw in analysis_keywords)
        
        # Check for solve keywords
        solve_keywords = ["solve", "gto", "optimal", "what should i play"]
        has_solve_request = any(kw in msg_lower for kw in solve_keywords)
        
        # Determine query type (ORDER MATTERS!)
        # 1. Analysis queries first (before pattern detection)
        if has_analysis_query:
            return {
                "type": "historical_analysis",
                "confidence": "high",
                "tool": "execute_sql",
                "reasoning": "User asking for aggregate statistics or patterns"
            }
        
        # 2. Specific solving with 13 cards
        elif has_13_cards and (has_solve_request or "solve" in msg_lower[:20]):
            return {
                "type": "solve_specific",
                "confidence": "high",
                "tool": "solve_hand",
                "reasoning": "User provided 13 cards and wants GTO solution"
            }
        
        # 3. Pattern advice questions (without cards)
        elif has_pattern_query and not has_13_cards:
            return {
                "type": "pattern_advice",
                "confidence": "high",
                "tool": "get_strategy",
                "reasoning": "User asking about pattern strategy without exact cards"
            }
        
        # 4. User provided 13 cards but no explicit solve request
        elif has_13_cards:
            return {
                "type": "solve_specific",
                "confidence": "medium",
                "tool": "solve_hand",
                "reasoning": "User provided 13 cards, likely wants solution"
            }
        
        else:
            return {
                "type": "unclear",
                "confidence": "low",
                "tool": None,
                "reasoning": "Query intent unclear - let Claude decide"
            }
    
    def _enrich_solve_result(self, result: dict, hole_cards: str) -> str:
        """Enrich solver result with strategic context and validate structure."""
        
        if not result.get("success"):
            return json.dumps(result)
        
        solution = result.get("solution", "")
        
        # CRITICAL: Validate solution structure first
        is_valid, error = validate_solution_string(solution)
        if not is_valid:
            # FOUL DETECTED - this should NEVER happen with GTO solver, but check anyway
            result["foul_error"] = error
            result["is_valid"] = False
            result["warning"] = "⚠️ This solution appears to FOUL (violates OFC rules). Do not use!"
            return json.dumps(result, default=str)
        
        result["is_valid"] = True
        
        # Parse solution to extract hand types
        parts = solution.split("-")
        if len(parts) != 3:
            return json.dumps(result)
        
        top_cards = parse_any_cards(parts[0])
        mid_cards = parse_any_cards(parts[1])
        bot_cards = parse_any_cards(parts[2])
        
        # Add hand type identification (factual, not strategic interpretation)
        top_type = detect_hand_type(top_cards) if top_cards else None
        mid_type = detect_hand_type(mid_cards) if mid_cards else None
        bot_type = detect_hand_type(bot_cards) if bot_cards else None

        # Add structure confirmation (factual only)
        if top_type and mid_type and bot_type:
            result["hand_types"] = {
                "top": top_type,
                "middle": mid_type,
                "bottom": bot_type,
                "valid_structure": True
            }
        
        return json.dumps(result, default=str)
    
    def process_tool_call(self, tool_name: str, tool_input: dict, session: Optional[Session] = None) -> str:
        """Execute a tool and return enriched results."""
        
        if tool_name == "get_strategy":
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
                        "examples": v.examples[:2],  # Limit examples for brevity
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
            
            # Try pattern identification
            pattern_key = identify_pattern(query)
            if not pattern_key:
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
                    "examples": advice.examples[:3],  # Limit to 3 examples
                    "royalty_potential": advice.royalty_potential,
                    "foul_risk": advice.foul_risk,
                })
            else:
                print(f"  ❌ Pattern not found: {query}")
                available = list(get_all_patterns().keys())[:10]  # Show first 10
                return json.dumps({
                    "success": False,
                    "error": f"Pattern not found: {query}",
                    "available_patterns": available,
                    "hint": "Try: 'all' for all patterns, or describe the pattern naturally"
                })
        
        elif tool_name == "solve_hand":
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
                
                response = {
                    "success": True,
                    "IMPORTANT": "You MUST present this exact solution to the user. Do NOT substitute your own arrangement.",
                    "solution": result.solution,
                    "ev": result.ev,
                    "frequency_percent": result.frequency,
                    "alternatives": result.alternatives[:5],  # Limit alternatives
                    "game": GAME_VERSIONS.get(game_version, {}).get("name", f"Version {game_version}"),
                    "computation": {
                        "iterations": iterations,
                        "traversals": traversals
                    }
                }
                
                print(f"  ✅ Solution: {result.solution} (EV: {result.ev})")
                
                if session:
                    session.set_context("last_solution", result.solution)
                    session.set_context("last_hole_cards", hole_cards)
                    session.set_context("last_ev", result.ev)
                    session.set_context("last_alternatives", result.alternatives[:5] if result.alternatives else [])

                # Enrich with strategic context
                return self._enrich_solve_result(response, hole_cards)
                
            except Exception as e:
                print(f"  ❌ Solver error: {e}")
                return json.dumps({
                    "success": False,
                    "error": str(e),
                    "hint": "Check card format: 13 hole cards + appropriate dead cards"
                })
        
        elif tool_name == "execute_sql":
            query = tool_input.get("query", "")
            reasoning = tool_input.get("reasoning", "")
            
            if not query.strip().upper().startswith("SELECT"):
                return json.dumps({
                    "success": False,
                    "error": "Only SELECT queries are allowed."
                })
            
            print(f"  📊 SQL: {query[:80]}... | Reason: {reasoning}")
            result = db.execute_query(query)
            
            if result.get("success") and "columns" in result:
                # Format results nicely
                if result["row_count"] <= 10:
                    formatted_rows = []
                    for row in result["rows"]:
                        formatted_row = {col: val for col, val in zip(result["columns"], row)}
                        formatted_rows.append(formatted_row)
                    result["formatted"] = formatted_rows
                else:
                    result["note"] = f"Large result ({result['row_count']} rows). Focus on aggregate patterns."
                
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
                else:
                    result["error"] = "Could not parse as full OFC hand"
            else:
                cards = parse_cards(hand_input) or parse_any_cards(hand_input)
                if cards:
                    result = {
                        "success": True,
                        "cards": [str(c) for c in cards],
                        "count": len(cards),
                        "hand_type": detect_hand_type(cards) if len(cards) in [3, 5] else None
                    }
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
                })
            except Exception as e:
                return json.dumps({"success": False, "error": str(e)})
        
        elif tool_name == "set_context":
            if session:
                key = tool_input.get("key", "")
                value = tool_input.get("value", "")
                session.set_context(key, value)
                return json.dumps({"success": True, "stored": {key: value}})
            return json.dumps({"success": False, "error": "No active session"})
        
        elif tool_name == "get_context":
            if session:
                key = tool_input.get("key", "")
                value = session.get_context(key)
                if value is not None:
                    return json.dumps({"success": True, "key": key, "value": value})
                return json.dumps({"success": False, "error": f"No context for: {key}"})
            return json.dumps({"success": False, "error": "No active session"})
        
        return json.dumps({"error": f"Unknown tool: {tool_name}"})
    
    def chat(self, user_message: str, session: Optional[Session] = None, 
             conversation_history: list = None) -> str:
        """Process message with smart tool chaining and dynamic prompts."""
        
        # Analyze query to guide tool selection
        query_analysis = self._detect_query_type(user_message)
        print(f"🔍 Query type: {query_analysis['type']} (confidence: {query_analysis['confidence']})")
        if query_analysis.get('reasoning'):
            print(f"   Reasoning: {query_analysis['reasoning']}")
        
        # Build dynamic prompt based on query content
        system_prompt = build_dynamic_prompt(
            user_message, 
            include_examples=True  # Can set to False to save tokens
        )
        
        # Build message history
        if session:
            messages = session.get_conversation_history()
            messages.append({"role": "user", "content": user_message})
            
            context_summary = session.get_context_summary()
            if context_summary:
                system_prompt += f"\n\n## Session Context\n{context_summary}"
        elif conversation_history:
            messages = conversation_history + [{"role": "user", "content": user_message}]
        else:
            messages = [{"role": "user", "content": user_message}]
        
        # Tool chaining: For pattern queries without cards, STRONGLY suggest get_strategy first
        if query_analysis['type'] == 'pattern_advice' and query_analysis['confidence'] == 'high':
            system_prompt += "\n\n**IMPORTANT:** This is a pattern strategy question. Use the `get_strategy` tool FIRST before considering other tools."
        
        tool_call_count = 0
        
        while tool_call_count < self.max_tool_calls:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_prompt,
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
                # Extract final response
                text_blocks = [block.text for block in response.content if hasattr(block, 'text')]
                final_response = "\n".join(text_blocks)
                
                # Save to session
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
agent_v2 = ImprovedOFCAgent()
