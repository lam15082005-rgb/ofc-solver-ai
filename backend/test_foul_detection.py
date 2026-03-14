"""Test foul detection and validation."""

import sys
from hand_validator import (
    validate_solution_string,
    validate_ofc_structure,
    format_hand_strength_comparison,
    get_hand_rank,
)


def test_hand_rankings():
    """Test basic hand ranking."""
    print("="*70)
    print("TEST 1: Hand Rankings")
    print("="*70)
    
    rankings = [
        ("High Card", 1),
        ("Pair", 2),
        ("Two Pair", 3),
        ("Trips", 4),
        ("Straight", 5),
        ("Flush", 6),
        ("Full House", 7),
        ("Quads", 8),
        ("Straight Flush", 9),
        ("Royal Flush", 10),
    ]
    
    all_pass = True
    for hand_type, expected_rank in rankings:
        actual_rank = get_hand_rank(hand_type)
        status = "✅" if actual_rank == expected_rank else "❌"
        print(f"{status} {hand_type}: {actual_rank} (expected {expected_rank})")
        if actual_rank != expected_rank:
            all_pass = False
    
    print(f"\n{'✅ All rankings correct!' if all_pass else '❌ Some rankings failed!'}\n")
    return all_pass


def test_structure_validation():
    """Test OFC structure validation."""
    print("="*70)
    print("TEST 2: Structure Validation")
    print("="*70)
    
    test_cases = [
        # (top, mid, bot, should_be_valid, description)
        ("High Card", "Pair", "Two Pair", True, "Valid: HC < Pair < 2P"),
        ("Pair", "Two Pair", "Trips", True, "Valid: Pair < 2P < Trips"),
        ("Pair", "Trips", "Full House", True, "Valid: Pair < Trips < FH"),
        ("Trips", "Pair", "Two Pair", False, "FOUL: Trips > Pair"),
        ("Pair", "Full House", "Trips", False, "FOUL: FH > Trips"),
        ("Two Pair", "Pair", "Trips", False, "FOUL: 2P > Pair"),
        ("High Card", "Straight", "Flush", True, "Valid: HC < Straight < Flush"),
        ("Flush", "Straight", "Full House", False, "FOUL: Flush > Straight"),
    ]
    
    all_pass = True
    for top, mid, bot, expected_valid, description in test_cases:
        is_valid, error = validate_ofc_structure(top, mid, bot)
        
        if is_valid == expected_valid:
            status = "✅"
        else:
            status = "❌"
            all_pass = False
        
        print(f"\n{status} {description}")
        print(f"   Top: {top}, Mid: {mid}, Bot: {bot}")
        print(f"   Result: {'VALID' if is_valid else 'FOUL'}")
        if error:
            print(f"   Error: {error}")
    
    print(f"\n{'✅ All structure tests passed!' if all_pass else '❌ Some structure tests failed!'}\n")
    return all_pass


def test_solution_validation():
    """Test full solution string validation."""
    print("="*70)
    print("TEST 3: Solution String Validation")
    print("="*70)
    
    test_cases = [
        # (solution, should_be_valid, description)
        ("AhAs5d-QhQd9s9c2h-KhKd7s7c4d", True, "Valid: Pair < 2P < 2P (KK77 > QQ99)"),
        ("KhQdJs-9h9d8s8c3h-AhAdKsKc7d", True, "Valid: HC < 2P < 2P"),
        ("QhQd5s-AhAdAcKd7s-KhKcKsQc9d", True, "Valid: Pair < Trips < FH"),
        ("2h2d2c-7h7d7cAs5d-AhAdAcKd9s", True, "Valid: Trips < Trips < FH (ascending)"),
        ("AhAdAc-KhKdKc7s2h-QhQd9s9c4h", False, "FOUL: Trips in middle, 2P on bottom (middle > bottom)"),
        ("KhKd5s-AhAdAc7s2h-QhJd9c8h7c", False, "FOUL: Pair on top, Trips in middle, HC on bottom"),
    ]
    
    all_pass = True
    for solution, expected_valid, description in test_cases:
        is_valid, error = validate_solution_string(solution)
        
        if is_valid == expected_valid:
            status = "✅"
        else:
            status = "❌"
            all_pass = False
        
        print(f"\n{status} {description}")
        print(f"   Solution: {solution}")
        print(f"   Result: {'VALID' if is_valid else 'FOUL'}")
        if error:
            print(f"   Error: {error}")
    
    print(f"\n{'✅ All solution tests passed!' if all_pass else '❌ Some solution tests failed!'}\n")
    return all_pass


def test_strength_comparison():
    """Test hand strength comparison formatting."""
    print("="*70)
    print("TEST 4: Strength Comparison Formatting")
    print("="*70)
    
    print("\nValid structure:")
    print(format_hand_strength_comparison("Pair", "Two Pair", "Trips"))
    
    print("\n" + "-"*50)
    print("\nFoul structure (Trips > Pair in middle):")
    print(format_hand_strength_comparison("Trips", "Pair", "Full House"))
    
    print("\n✅ Formatting test complete!\n")
    return True


def main():
    """Run all tests."""
    print("\n🧪 OFC FOUL DETECTION TESTS\n")
    
    try:
        results = []
        results.append(("Hand Rankings", test_hand_rankings()))
        results.append(("Structure Validation", test_structure_validation()))
        results.append(("Solution Validation", test_solution_validation()))
        results.append(("Strength Comparison", test_strength_comparison()))
        
        print("="*70)
        print("TEST SUMMARY")
        print("="*70)
        for test_name, passed in results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status} - {test_name}")
        
        all_passed = all(r[1] for r in results)
        
        if all_passed:
            print("\n✅ ALL TESTS PASSED! Foul detection is working correctly.\n")
            return 0
        else:
            print("\n❌ SOME TESTS FAILED! Review output above.\n")
            return 1
            
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
