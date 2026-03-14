"""Quick test of the solver-first agent."""

import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Test solver directly first
print("=" * 60)
print("Testing solver module directly...")
print("=" * 60)

from solver import solve_hand

# Simple test
hole = "Ah Kd Qc Js Th 9c 8d 7s 6h 5c 4d 3s 2h"
dead = "As Ks Qs Jd"

print(f"\nHole cards: {hole}")
print(f"Dead cards: {dead}")
print("Solving with 2000 iterations...")

result = solve_hand(hole, dead, game_version=2, iterations=2000, traversals=50)

print(f"\n✅ GTO Solution: {result.solution}")
print(f"   EV: {result.ev}")
print(f"   Frequency: {result.frequency}%")
print(f"\nTop 3 alternatives:")
for i, alt in enumerate(result.alternatives[:3], 1):
    print(f"   {i}. {alt['solution']}")
    print(f"      EV: {alt['ev']}, Freq: {alt['frequency']}%")

print("\n" + "=" * 60)
print("Solver test complete!")
print("=" * 60)

# Optionally test agent if API key is available
if os.getenv('ANTHROPIC_API_KEY'):
    print("\n\nTesting agent chat (if this hangs, the API call is running)...")
    from agent import agent
    
    test_message = f"Solve this hand: {hole} with dead cards {dead}"
    print(f"\nUser: {test_message}")
    print("Agent: (computing...)")
    
    # This will actually call Claude and the solver
    # response = agent.chat(test_message)
    # print(f"Agent: {response[:500]}...")
    print("(Skipping actual agent test to save API calls)")
else:
    print("\n⚠️ ANTHROPIC_API_KEY not set - skipping agent test")
