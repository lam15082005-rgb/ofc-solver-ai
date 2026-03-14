#!/usr/bin/env python3
"""CLI for testing the OFC Solver AI agent."""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from agent import agent
from session import session_manager, Session
from hand_parser import parse_ofc_hand, parse_cards
from visualizer import render_solution, render_ofc_hand


def print_help():
    """Print available commands."""
    print("""
📚 Available Commands:
  /help          - Show this help message
  /quit, /exit   - Exit the CLI
  /new           - Start a new session (clears context)
  /context       - Show current session context
  /clear         - Clear session context
  /viz <hand>    - Visualize a hand (e.g., /viz Jh4s3h-As5c4c3c2h-KdJd9d7d3d)
  /parse <cards> - Parse and display cards
  /sessions      - List saved sessions
  /load <id>     - Load a previous session
  
💡 Example Questions:
  - "Show me a solution with pair of aces on top"
  - "I have AdKhQsJcTc, what are my options?"
  - "What's the GTO play for this hand: AhAs-KdQdJdTd9d-8c8d7c7d6c"
  - "Compare joker vs non-joker solutions"
  - "What's the average EV for hands with a flush bottom?"
""")


def handle_command(command: str, session: Session) -> tuple[bool, Session]:
    """
    Handle CLI commands.
    
    Returns:
        Tuple of (should_continue, session)
    """
    parts = command.split(maxsplit=1)
    cmd = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else ""
    
    if cmd in ('/quit', '/exit', '/q'):
        print("👋 Goodbye!")
        return False, session
    
    elif cmd == '/help':
        print_help()
    
    elif cmd == '/new':
        session = session_manager.create_session()
        print(f"🆕 New session created: {session.session_id}")
    
    elif cmd == '/context':
        if session.context:
            print("📋 Current Context:")
            for key, value in session.context.items():
                print(f"  {key}: {value}")
        else:
            print("📋 No context stored yet.")
    
    elif cmd == '/clear':
        session.clear_context()
        print("🧹 Context cleared.")
    
    elif cmd == '/viz':
        if not arg:
            print("Usage: /viz <solution>")
            print("Example: /viz Jh4s3h-As5c4c3c2h-KdJd9d7d3d")
        else:
            print(render_solution(arg))
    
    elif cmd == '/parse':
        if not arg:
            print("Usage: /parse <cards>")
            print("Example: /parse AhKdQs or /parse Ah Kd Qs")
        else:
            hand = parse_ofc_hand(arg)
            if hand:
                print(render_ofc_hand(hand))
            else:
                cards = parse_cards(arg)
                if cards:
                    from visualizer import render_cards_row
                    print(render_cards_row(cards))
                else:
                    print("❌ Could not parse input")
    
    elif cmd == '/sessions':
        sessions = session_manager.list_sessions()
        if sessions:
            print("📁 Saved Sessions:")
            for sid in sessions:
                print(f"  - {sid}")
        else:
            print("No saved sessions found.")
    
    elif cmd == '/load':
        if not arg:
            print("Usage: /load <session_id>")
        else:
            loaded = session_manager.get_session(arg)
            if loaded:
                session = loaded
                print(f"✅ Loaded session: {session.session_id}")
                print(f"   Messages: {len(session.messages)}")
                if session.context:
                    print(f"   Context: {list(session.context.keys())}")
            else:
                print(f"❌ Session not found: {arg}")
    
    else:
        print(f"Unknown command: {cmd}")
        print("Type /help for available commands.")
    
    return True, session


def main():
    print("🎴 OFC Solver AI - CLI Mode")
    print("=" * 40)
    print("Ask questions about GTO poker strategy.")
    print("Type /help for commands, /quit to exit.\n")
    
    # Create or load session
    session = session_manager.create_session()
    print(f"📍 Session: {session.session_id}\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Goodbye!")
            break
        
        if not user_input:
            continue
        
        # Handle exit/quit without slash
        if user_input.lower() in ('quit', 'exit', 'q'):
            print("👋 Goodbye!")
            break
        
        # Handle commands
        if user_input.startswith('/'):
            should_continue, session = handle_command(user_input, session)
            if not should_continue:
                break
            continue
        
        # Regular chat
        print("\n🤔 Thinking...")
        try:
            response = agent.chat(user_input, session=session)
            print(f"\n🤖 Agent:\n{response}\n")
            
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
