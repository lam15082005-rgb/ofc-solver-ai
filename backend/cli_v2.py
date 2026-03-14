"""CLI interface for testing improved OFC Solver AI agent v2."""

import sys
from agent_v2 import agent_v2 as agent
from session import session_manager


def print_banner():
    print("\n" + "="*70)
    print("  OFC SOLVER AI - Improved Agent v2")
    print("  Type 'quit' or 'exit' to exit")
    print("  Type 'new' to start a new session")
    print("="*70 + "\n")


def main():
    print_banner()
    
    # Create or load session
    session = session_manager.create_session()
    print(f"Session: {session.session_id}\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye! 👋\n")
                break
            
            if user_input.lower() == 'new':
                session = session_manager.create_session()
                print(f"\n✨ New session: {session.session_id}\n")
                continue
            
            # Get response from improved agent
            print()  # Blank line for readability
            response = agent.chat(user_input, session)
            
            print(f"\n🦞 Agent v2:\n{response}\n")
            
        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye! 👋\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
