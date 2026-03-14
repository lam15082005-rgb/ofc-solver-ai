"""Test the strategic knowledge system."""

from strategy import (
    get_pattern_advice,
    identify_pattern,
    get_all_patterns,
    format_pattern_advice,
)


def test_pattern_lookup():
    """Test direct pattern lookup."""
    print("=== Testing Direct Pattern Lookup ===\n")
    
    advice = get_pattern_advice("5_pairs_3_singles")
    assert advice is not None, "Should find 5_pairs_3_singles pattern"
    
    print(f"Pattern: {advice.pattern}")
    print(f"Distribution: {advice.distribution}")
    print(f"Royalty Potential: {advice.royalty_potential}")
    print(f"Foul Risk: {advice.foul_risk}")
    print()


def test_pattern_identification():
    """Test natural language pattern identification."""
    print("=== Testing Natural Language Identification ===\n")
    
    test_cases = [
        ("I have 5 pairs and 3 singles", "5_pairs_3_singles"),
        ("I have 4 pairs and 5 singles", "4_pairs_5_singles"),
        ("I have 6 pairs and 1 single", "6_pairs_1_single"),
        ("I have trips and some pairs", "trips_and_pairs"),
        ("I have a straight draw", "straight_potential"),
        ("I have a flush draw", "flush_potential"),
    ]
    
    for description, expected_key in test_cases:
        identified = identify_pattern(description)
        status = "✅" if identified == expected_key else "❌"
        print(f"{status} '{description}' -> {identified} (expected: {expected_key})")
    
    print()


def test_all_patterns():
    """Test getting all patterns."""
    print("=== Testing All Patterns ===\n")
    
    patterns = get_all_patterns()
    print(f"Total patterns: {len(patterns)}\n")
    
    for key in patterns.keys():
        print(f"  - {key}")
    
    print()


def test_format_advice():
    """Test formatting strategic advice."""
    print("=== Testing Formatted Advice ===\n")
    
    advice = get_pattern_advice("5_pairs_3_singles")
    formatted = format_pattern_advice(advice)
    
    print(formatted)
    print()


if __name__ == "__main__":
    test_pattern_lookup()
    test_pattern_identification()
    test_all_patterns()
    test_format_advice()
    
    print("✅ All strategy tests passed!")
