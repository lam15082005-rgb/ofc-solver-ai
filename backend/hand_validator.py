"""Hand validation to prevent suggesting illegal/fouling hands."""

from typing import List, Optional, Tuple
from hand_parser import parse_any_cards, detect_hand_type


# Hand strength rankings (lower = weaker)
HAND_RANKINGS = {
    "High Card": 1,
    "Pair": 2,
    "Two Pair": 3,
    "Trips": 4,
    "Three of a Kind": 4,  # Alias
    "Straight": 5,
    "Flush": 6,
    "Full House": 7,
    "Quads": 8,
    "Four of a Kind": 8,  # Alias
    "Straight Flush": 9,
    "Royal Flush": 10,
    "Five of a Kind": 11,  # Joker games only
}


def get_hand_rank(hand_type: str) -> int:
    """Get numeric rank for a hand type. Returns 0 if unknown."""
    return HAND_RANKINGS.get(hand_type, 0)


def validate_ofc_structure(top_type: str, mid_type: str, bot_type: str) -> Tuple[bool, Optional[str]]:
    """
    Validate that an OFC hand structure follows the rules: top < middle < bottom.
    
    Returns:
        (is_valid, error_message)
        - is_valid: True if structure is legal, False if it fouls
        - error_message: None if valid, error description if invalid
    """
    top_rank = get_hand_rank(top_type)
    mid_rank = get_hand_rank(mid_type)
    bot_rank = get_hand_rank(bot_type)
    
    # Unknown hand types
    if top_rank == 0 or mid_rank == 0 or bot_rank == 0:
        return True, None  # Can't validate unknown types, assume valid
    
    # Check top < middle
    if top_rank > mid_rank:
        return False, f"❌ FOUL: Top ({top_type}) is stronger than Middle ({mid_type})"
    
    # Check middle < bottom
    if mid_rank > bot_rank:
        return False, f"❌ FOUL: Middle ({mid_type}) is stronger than Bottom ({bot_type})"
    
    # Check top < bottom (transitive, but explicit for clarity)
    if top_rank > bot_rank:
        return False, f"❌ FOUL: Top ({top_type}) is stronger than Bottom ({bot_type})"
    
    return True, None


def validate_solution_string(solution: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a solution string (format: "Top-Middle-Bottom").
    
    Returns:
        (is_valid, error_message)
    """
    parts = solution.split("-")
    if len(parts) != 3:
        return True, None  # Can't parse, skip validation
    
    # Parse cards
    top_cards = parse_any_cards(parts[0])
    mid_cards = parse_any_cards(parts[1])
    bot_cards = parse_any_cards(parts[2])
    
    if not top_cards or not mid_cards or not bot_cards:
        return True, None  # Can't parse cards, skip validation
    
    # Check card counts
    if len(top_cards) != 3:
        return False, f"❌ INVALID: Top must have exactly 3 cards (has {len(top_cards)})"
    if len(mid_cards) != 5:
        return False, f"❌ INVALID: Middle must have exactly 5 cards (has {len(mid_cards)})"
    if len(bot_cards) != 5:
        return False, f"❌ INVALID: Bottom must have exactly 5 cards (has {len(bot_cards)})"
    
    # Detect hand types
    top_type = detect_hand_type(top_cards)
    mid_type = detect_hand_type(mid_cards)
    bot_type = detect_hand_type(bot_cards)
    
    if not top_type or not mid_type or not bot_type:
        return True, None  # Can't determine types, skip validation
    
    # Validate structure
    return validate_ofc_structure(top_type, mid_type, bot_type)


def add_foul_warning(result: dict) -> dict:
    """
    Add foul validation to a solver/strategy result.
    Modifies result in-place and returns it.
    """
    solution = result.get("solution", "")
    if not solution:
        return result
    
    is_valid, error = validate_solution_string(solution)
    
    if not is_valid:
        result["foul_warning"] = error
        result["is_valid"] = False
        # Make it VERY obvious
        if "strategic_context" in result:
            result["strategic_context"].insert(0, error)
        else:
            result["strategic_context"] = [error]
    else:
        result["is_valid"] = True
    
    return result


def format_hand_strength_comparison(top_type: str, mid_type: str, bot_type: str) -> str:
    """Format a visual comparison of hand strengths."""
    top_rank = get_hand_rank(top_type)
    mid_rank = get_hand_rank(mid_type)
    bot_rank = get_hand_rank(bot_type)
    
    lines = [
        "Hand Strength Check:",
        f"  Top:    {top_type} (rank {top_rank})",
        f"  Middle: {mid_type} (rank {mid_rank})",
        f"  Bottom: {bot_type} (rank {bot_rank})",
    ]
    
    if top_rank <= mid_rank <= bot_rank:
        lines.append("  ✅ Valid structure (top < middle < bottom)")
    else:
        lines.append("  ❌ FOUL - Invalid structure!")
        if top_rank > mid_rank:
            lines.append("     Top is stronger than Middle!")
        if mid_rank > bot_rank:
            lines.append("     Middle is stronger than Bottom!")
    
    return "\n".join(lines)


if __name__ == "__main__":
    # Test cases
    print("Testing OFC Hand Validator\n")
    
    test_cases = [
        ("AAx-QQ99x-KK77x", "Valid - pair top, two-pair mid/bot"),
        ("KKK-AAQQx-AAKKx", "FOUL - trips on top stronger than two-pair middle"),
        ("AKQ-QQ99x-KK77x", "Valid - high card, two-pair, two-pair"),
        ("QQx-AAAKx-KKKQx", "Valid - pair, trips, full house"),
        ("AAAx-KKKQx-QQ99x", "FOUL - trips top > full house mid > two-pair bot"),
    ]
    
    for solution, description in test_cases:
        print(f"\nTest: {description}")
        print(f"Solution: {solution}")
        is_valid, error = validate_solution_string(solution)
        if is_valid:
            print("✅ VALID")
        else:
            print(f"❌ {error}")
