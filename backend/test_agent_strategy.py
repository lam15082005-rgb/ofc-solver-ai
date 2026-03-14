"""Test the agent's strategic advice capability."""

import json
from agent import agent


def test_strategy_query():
    """Test asking the agent about a pattern without cards."""
    
    print("=== Testing Agent Strategy Query ===\n")
    
    query = "If I have 5 pairs and 3 singles, how should I play it?"
    
    print(f"User: {query}\n")
    
    response = agent.chat(query)
    
    print(f"Agent: {response}\n")
    
    # Verify the response mentions key concepts
    assert "pair" in response.lower(), "Response should mention pairs"
    assert "top" in response.lower(), "Response should mention top hand"
    assert "middle" in response.lower(), "Response should mention middle hand"
    assert "bottom" in response.lower(), "Response should mention bottom hand"
    
    print("✅ Agent successfully provided strategic advice!\n")


def test_multiple_patterns():
    """Test asking about different patterns."""
    
    print("=== Testing Multiple Patterns ===\n")
    
    queries = [
        "What if I have trips and a pair?",
        "How do I play a flush draw?",
        "What's the best way to arrange 4 pairs and 5 singles?",
    ]
    
    for query in queries:
        print(f"\nUser: {query}")
        response = agent.chat(query)
        print(f"Agent: {response[:200]}...")  # First 200 chars
        print()


if __name__ == "__main__":
    test_strategy_query()
    test_multiple_patterns()
    
    print("✅ All agent strategy tests passed!")
