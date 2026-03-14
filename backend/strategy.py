"""Strategic knowledge base for OFC poker patterns and optimal play heuristics.

This module provides high-level strategic guidance for common hand patterns,
allowing the AI to give advice without needing exact cards or solver runs.

Data-driven insights are imported from strategy_data.py, which contains
analysis of 327k+ GTO-solved hands from the CFR database.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# Import data-driven insights
from strategy_data import (
    TOP_PAIR_EV,
    TRIPS_PLACEMENT_EV,
    MIDDLE_VS_BOTTOM_EV,
    BOTTOM_ROW_EV,
    DATA_DRIVEN_PRINCIPLES,
    get_all_insights as get_data_insights,
)


@dataclass
class StrategyAdvice:
    """Strategic advice for a hand pattern."""
    pattern: str
    distribution: str
    reasoning: str
    examples: List[str]
    royalty_potential: str
    foul_risk: str


# Core strategic patterns
BASIC_PATTERNS = {
    "5_pairs_3_singles": StrategyAdvice(
        pattern="5 Pairs + 3 Singles",
        distribution="HIGHEST pair on top, then split remaining 4 pairs to create THREE STRONG HANDS",
        reasoning="""With 5 pairs, maximize royalties AND row wins by building three competitive hands.
        - Put your HIGHEST pair on top (stronger pair = wins more often, pair on top = 1 pt royalty)
        - Split remaining 4 pairs BALANCED - don't dump strength into one row
        - Goal: Three hands that can each win their row, not one super-strong + one weak
        - Example with AA, KK, QQ, 99, 77: Put AA top, then QQ99 middle, KK77 bottom
          - This beats: AAx-9977x-KKQQx (weak middle loses too often)
        - Two-pair is ranked by highest pair: KK77 > QQ99 > 9977""",
        examples=[
            "AAx-QQ99x-KK77x (AA top, balanced QQ/KK two-pairs = 3 strong hands)",
            "KKx-QQ88x-AA99x (KK top, balanced middle/bottom)",
            "QQx-9977x-AAKKx (QQ top, only option when AA/KK needed for bottom strength)"
        ],
        royalty_potential="Medium - Pair on top = 1 pt royalty; two-pair in middle/bottom = 1 pt each",
        foul_risk="Very Low - Pairs guarantee ascending hand strength"
    ),
    
    "4_pairs_5_singles": StrategyAdvice(
        pattern="4 Pairs + 5 Singles",
        distribution="High card on top, Two Pair in middle, Two Pair on bottom",
        reasoning="""You have 4 pairs but 5 singles, so you can't put a pair on top.
        - Use 3 highest singles on top (aim for high card royalties if A or K high)
        - Put WEAKER two-pair in middle, STRONGER two-pair on bottom
        - Add single kickers to each
        - Remember: bottom must beat middle!""",
        examples=[
            "AKT-8866x-QQJJx (A-high top, 88s up middle, QQs up bottom)",
            "KQJ-7755x-AAKKx (K-high top, 77s up middle, AAs up bottom)",
        ],
        royalty_potential="Low - High card top = 1 pt royalty",
        foul_risk="Low - Even distribution prevents fouling"
    ),
    
    "6_pairs_1_single": StrategyAdvice(
        pattern="6 Pairs + 1 Single",
        distribution="Pair on top, Two Pair in middle, Two Pair on bottom (break one pair for kickers)",
        reasoning="""With 6 pairs and only 1 single, you need to break one pair for kickers.
        - Put a HIGH pair on top for royalties (QQ/KK/AA)
        - Use the single + one card from a broken pair as kickers for middle/bottom
        - Put WEAKER two-pair in middle, STRONGER two-pair on bottom
        - This gives you pair royalties on top + strong two-pair structure""",
        examples=[
            "QQx-JJ99x-AAKKx (QQ on top for royalties, break one pair for kickers)",
            "AA5-9988T-KKQQx (AA on top for max royalties, 99s up middle, KKs up bottom)",
            "KKx-TT99x-AAQQx (KK on top, TTs up middle, AAs up bottom)",
        ],
        royalty_potential="Medium - All pairs on top = 1 pt royalty; stronger pairs win more rows",
        foul_risk="Low - Abundant pairs prevent fouling"
    ),
    
    "3_trips": StrategyAdvice(
        pattern="3 Trips (9 matching cards)",
        distribution="Trips on top, Trips in middle, Trips on bottom",
        reasoning="""Extremely rare but extremely powerful.
        - Put HIGHEST trips on BOTTOM (for maximum bottom strength)
        - Put MEDIUM trips in MIDDLE (for middle strength)
        - Put LOWEST trips on TOP (for top royalties - trips on top = 3 pts)
        - This ascending structure is automatic and maximizes all three rows
        - Remaining 4 cards: use as kickers; if any form quads, put quads in middle (8 pts!)""",
        examples=[
            "222-777Ax-AAAKx (ascending trips)",
            "333-888Kx-KKKAx",
        ],
        royalty_potential="High - Trips on top (3 pts), trips in middle (1 pt), trips on bottom (1 pt). If quads possible in middle: 8 pts!",
        foul_risk="None - Trips are always in ascending order"
    ),
    
    "trips_and_pairs": StrategyAdvice(
        pattern="1 Trips + Multiple Pairs",
        distribution="Pair on top, Two Pair/Trips in middle, Full House/Trips on bottom",
        reasoning="""Trips give you full house potential.
        - If you can make a FULL HOUSE on bottom (trips + pair), do it (high royalties)
        - Put a PAIR on top (preferably high for royalties)
        - Middle can be trips or two-pair depending on remaining cards
        - Prioritize full house on bottom > trips in middle""",
        examples=[
            "998-QQ754-KKKJJ (full house bottom, pair middle, weaker pair top)",
            "JJ9-QQ753-AAAKK (full house bottom, higher pair middle, lower pair top)",
        ],
        royalty_potential="Medium - Full house on bottom (1 pt), trips middle (1 pt), pair top (1 pt). Better than average!",
        foul_risk="Low-Medium - Need to ensure middle beats top but loses to bottom"
    ),
    
    "straight_potential": StrategyAdvice(
        pattern="Straight Draw (9+ cards in sequence range)",
        distribution="Depends on completed straight location",
        reasoning="""Straights require 5 cards in sequence.
        - If you can make a STRAIGHT on BOTTOM + high cards elsewhere: do it
        - WHEEL (A-2-3-4-5) is powerful but low-ranking straight
        - Broadway (T-J-Q-K-A) is the nut straight
        - Middle straight may be suboptimal - straights are more valuable on bottom (royalties)
        - Avoid wasting straight cards on top (only 3 cards, can't complete)""",
        examples=[
            "K85-QQ994-AKQJT (broadway straight on bottom, pair in middle, high top)",
            "KK7-98643-A2345 (wheel on bottom, high card middle, pair top)",
        ],
        royalty_potential="Low-Medium - Bottom straight = 1 pt, high card top = 1 pt",
        foul_risk="Medium - Straights lock 5 cards; remaining 8 must still satisfy top < middle"
    ),
    
    "flush_potential": StrategyAdvice(
        pattern="Flush Draw (5+ cards of same suit)",
        distribution="Flush on bottom if possible, high cards elsewhere",
        reasoning="""Flushes require 5+ cards of the same suit.
        - ALWAYS put flush on BOTTOM (2-4 royalty points)
        - Use remaining cards for top (pair or high) and middle (pair/trips/straight)
        - If you have 8+ cards of one suit, consider using 3 for top (no flush possible on top)
        - Flush > Straight in both strength and royalty value""",
        examples=[
            "AKQ-8877-Ah5h3h2hTh (flush on bottom, pairs middle, high top)",
            "KK-AJT98-7h6h5h4h2h (flush on bottom, pair top)",
        ],
        royalty_potential="Low-Medium - Bottom flush = 1 pt. If quads available, middle quads = 8 pts!",
        foul_risk="Medium - Flush locks 5 cards of one suit; need strong remaining 8"
    ),
    
    "high_cards_only": StrategyAdvice(
        pattern="All High Cards (no pairs/straights/flushes)",
        distribution="Top: 3 highest, Middle: next 5 highest, Bottom: 5 lowest (but still high)",
        reasoning="""No made hands = high-foul risk.
        - Distribute HIGH CARDS from top to bottom in DESCENDING order
        - Top: A-K-Q (best high card hand)
        - Middle: K-Q-J-T-9 (second-best high card hand)
        - Bottom: J-T-9-8-7 (worst high card hand but still beats middle)
        - This guarantees no foul
        - No royalties likely unless top is A-high (3 pts) or K-high (2 pts)""",
        examples=[
            "AKQ-AKJTx-QJT9x (descending high cards)",
        ],
        royalty_potential="Low - High card top = 1 pt royalty",
        foul_risk="High - No pairs to guarantee structure; must carefully order by high card"
    ),
    
    "low_cards_spread": StrategyAdvice(
        pattern="Mostly Low Cards (7 or below)",
        distribution="Focus on making the best possible middle/bottom; top will be weak",
        reasoning="""Low cards make royalties unlikely.
        - Focus on NOT FOULING
        - Look for any pairs (even 22) and put on top
        - Try to make two-pair or trips if possible
        - Accept that royalties are unlikely; just beat opponents or minimize loss""",
        examples=[
            "665-44332-77543 (pair top, two-pair middle, two-pair bottom)",
        ],
        royalty_potential="Very Low - Bottom trips = 1 pt, pair on top = 1 pt",
        foul_risk="High - Weak cards make it hard to build ascending hands"
    ),
}


# Royalty tables - MUST match the C++ solver's actual scoring (OFCRewarder.cpp)
# These are the ACTUAL game royalties used in CFR computation.
# WARNING: Do NOT change these without also updating OFCRewarder.cpp
ROYALTY_POINTS = {
    "top": {
        "high_card": 1,
        "pair": 1,       # All pairs score the same (1 pt)
        "trips": 3,      # All trips score the same (3 pts)
    },
    "middle": {
        "high_card": 1,
        "pair": 1,
        "two_pair": 1,
        "trips": 1,
        "straight": 1,
        "flush": 1,
        "full_house": 2,
        "quads": 8,       # Quads in middle = 8 pts (very valuable!)
        "straight_flush": 10,
        "five_of_a_kind": 16,
    },
    "bottom": {
        "high_card": 1,
        "pair": 1,
        "two_pair": 1,
        "trips": 1,
        "straight": 1,
        "flush": 1,
        "full_house": 1,
        "quads": 4,       # Quads on bottom = 4 pts
        "straight_flush": 5,
        "five_of_a_kind": 8,
    }
}


# Strategic principles
STRATEGIC_PRINCIPLES = {
    "royalty_maximization": """
    Royalty Maximization (actual solver values from OFCRewarder.cpp):
    - TOP: Pair = 1, Trips = 3
    - MIDDLE: Trips = 1, Full House = 2, Quads = 8, Straight Flush = 10, Five of a Kind = 16
    - BOTTOM: Quads = 4, Straight Flush = 5, Five of a Kind = 8

    Priority:
    1. Don't foul (lose everything)
    2. Maximize TOTAL royalties across all three rows
    3. Win rows against opponents

    Key insight: Quads in MIDDLE (8 pts) is worth DOUBLE quads on BOTTOM (4 pts).
    When you can make quads, placing them in middle is hugely valuable.
    """,
    
    "foul_avoidance": """
    Fouling Prevention:
    A foul occurs when hands are not in ascending order: Top < Middle < Bottom
    
    Common foul scenarios:
    - Putting a strong pair on top but weak high cards in middle
    - Making trips in middle but only two-pair on bottom
    - Building a flush on bottom but accidentally making a straight in middle
    
    Safe structures:
    - Pair / Two-Pair / Two-Pair (with higher pairs on bottom)
    - High card / Pair / Two-Pair
    - Pair / Trips / Full House
    - High card / Two-Pair / Straight or Flush
    
    When in doubt: Use pairs to build a safe structure (pair/2pair/2pair is never a foul if properly ordered).
    """,
    
    "hand_reading": """
    Reading Your Hand Pattern:
    
    1. Count pairs: How many pairs do you have? (0-6 possible)
    2. Count trips: Do you have any three-of-a-kinds? (0-3 possible, but 3 is extremely rare)
    3. Check straight potential: Do you have 5+ cards in sequence?
    4. Check flush potential: Do you have 5+ cards of the same suit?
    5. Check quads: Do you have four-of-a-kind? (rare, but powerful)
    
    Hierarchy of made hands (from weakest to strongest):
    - High card
    - One pair
    - Two pair
    - Three of a kind (trips)
    - Straight
    - Flush
    - Full house
    - Four of a kind (quads)
    - Straight flush
    - Royal flush (A-K-Q-J-T suited)
    
    Distribution logic:
    - Strongest hand → Bottom
    - Medium hand → Middle
    - Weakest hand → Top
    - But remember: Top has HIGHER royalty multipliers for pairs/trips!
    """,
    
    "joker_strategy": """
    Playing With Jokers (Versions 2, 4-7):

    Jokers are WILD cards (can be any card).

    Optimal joker usage:
    1. Complete a strong hand (straight, flush, full house)
    2. Make quads (four-of-a-kind = high royalties, especially in middle)
    3. Upgrade trips to quads or full house
    4. Complete a flush/straight for hand strength

    Where to use jokers:
    - MIDDLE: Quads in middle = 8 pts (highest non-SF royalty)
    - BOTTOM: Quads on bottom = 4 pts, straight flush = 5 pts
    - TOP: Trips on top = 3 pts; with 2 jokers = 10 pts, with 3 jokers = 20 pts (V2 special bonus)

    Example:
    - *+AAA = Quad Aces (8 pts in middle, 4 pts on bottom)
    - *+KK in top = Trips Kings (3 pts on top, or 10 pts with 2 jokers in V2)
    """,
    
    "expected_value": """
    EV (Expected Value) Thinking:
    
    EV = average points gained/lost over infinite trials
    
    Key factors:
    1. Royalty points (guaranteed bonuses)
    2. Row win probability (comparing against random opponent hands)
    3. Scoop probability (winning all three rows = +6 bonus)
    4. Foul probability (fouling = -6 penalty)
    
    Trade-offs:
    - High royalty chasing (e.g., trying for a flush) vs safe structure (guaranteed pairs)
    - Top royalties (trips=3 pts) vs middle royalties (quads=8 pts) vs bottom royalties (quads=4 pts)

    The solver computes exact EV using CFR — always trust solver output for specific hands.
    Strategic heuristics:
    - Safe pair/pair/pair structures have positive EV floor (won't foul)
    - Chasing big hands (straights/flushes) risks fouling if they don't hit
    - Middle quads (8 pts) is the highest royalty target outside of straight flushes
    """,
    
    # =========================================================================
    # DATA-DRIVEN INSIGHTS (from 327k+ solved hands)
    # =========================================================================
    
    "data_top_pair_selection": """
    DATA-DRIVEN: Top Pair Selection (327k hands analyzed)

    Average EV by top pair:
    - AA on top: -1.19 EV (BEST)
    - KK on top: -4.40 EV (3.2 points worse than AA!)
    - QQ on top: -5.45 EV (1.0 worse than KK)
    - JJ on top: -7.28 EV
    - TT on top: -7.65 EV

    HEURISTIC: Higher pairs on top tend to perform better because they win the row more often
    (all pairs earn the same 1 pt royalty, but winning earns the royalty while losing doesn't).

    TRIPS ON TOP: +25.16 average EV — generally very strong, but always defer to solver for specific hands.
    """,
    
    "data_trips_placement": """
    DATA-DRIVEN: Trips Placement (327k hands analyzed)

    Average EV by trips position:
    - Trips on TOP: +25.16 EV (generally profitable)
    - Trips in MIDDLE: -8.49 EV
    - Trips on BOTTOM: -16.58 EV

    DIFFERENCE: ~33-42 EV swing between top and other positions!

    WHY? Top trips (3 pts royalty) + winning top row more often = high EV.
    BUT this is an average heuristic. When you can make quads in middle (8 pts!)
    instead of trips in middle (1 pt), the quads arrangement may be better.
    Always defer to the solver's computed result for specific hands.
    """,
    
    "data_premium_placement": """
    DATA-DRIVEN: Premium Hands Placement (327k hands analyzed)

    CORRELATION (NOT CAUSATION!):

                        MIDDLE      BOTTOM
    Quads:              +42.83      +5.86
    Full House:         +10.50      -8.69
    Flush:              +0.65       -9.72

    WHY the EV difference? Because middle must be WEAKER than bottom!
    - Flush in middle → you MUST have full house/quads/SF on bottom
    - So "flush in middle" = "I have TWO premium hands"
    - The high EV comes from having multiple premium hands

    CORRECT INTERPRETATION:
    - If you have ONE premium hand → it goes on bottom (only valid option)
    - If you have TWO premium hands → weaker in middle, stronger on bottom
    - Multiple premium hands = very profitable (the actual insight!)

    ROYALTY NOTE: Middle quads = 8 pts vs bottom quads = 4 pts (actual solver values).
    When you can make quads in middle, it's worth double the bottom royalty.
    """,
    
    "data_balanced_structure": """
    DATA-DRIVEN: Three Strong Hands Principle (327k hands analyzed)
    
    Analysis confirms: Balanced structures beat "dump strength into bottom"
    
    Example with 5 pairs (AA, KK, QQ, 99, 77):
    
    WRONG: KK-9977-AAQQ
    - Top: KK (8 pts) | Middle: 9977 (weak) | Bottom: AAQQ (strong)
    - Problem: Weak middle loses too many rows
    
    RIGHT: AA-QQ99-KK77
    - Top: AA (9 pts, +1) | Middle: QQ99 (competitive) | Bottom: KK77 (wins most)
    - Result: +1 royalty AND better row win rate overall
    
    RULE: Maximize top royalties first, then build balanced middle/bottom.
    Don't sacrifice middle strength for an overly-strong bottom.
    """
}


def get_pattern_advice(pattern_key: str) -> Optional[StrategyAdvice]:
    """Get strategic advice for a specific pattern."""
    return BASIC_PATTERNS.get(pattern_key)


def identify_pattern(description: str) -> Optional[str]:
    """
    Identify a pattern key from a natural language description.
    
    Args:
        description: User's description (e.g., "I have 5 pairs and 3 singles")
    
    Returns:
        Pattern key if identified, None otherwise
    """
    desc_lower = description.lower()
    
    # Pairs + singles patterns
    if "5" in desc_lower and "pair" in desc_lower and "3" in desc_lower and "single" in desc_lower:
        return "5_pairs_3_singles"
    if "4" in desc_lower and "pair" in desc_lower and "5" in desc_lower and "single" in desc_lower:
        return "4_pairs_5_singles"
    if "6" in desc_lower and "pair" in desc_lower and "1" in desc_lower and "single" in desc_lower:
        return "6_pairs_1_single"
    
    # Trips patterns
    if "3" in desc_lower and ("trip" in desc_lower or "three of a kind" in desc_lower):
        return "3_trips"
    if ("trip" in desc_lower or "three of a kind" in desc_lower) and "pair" in desc_lower:
        return "trips_and_pairs"
    
    # Draw patterns
    if "straight" in desc_lower and ("draw" in desc_lower or "potential" in desc_lower):
        return "straight_potential"
    if "flush" in desc_lower and ("draw" in desc_lower or "potential" in desc_lower):
        return "flush_potential"
    
    # Weak patterns
    if "high card" in desc_lower and "only" in desc_lower:
        return "high_cards_only"
    if "low" in desc_lower and "card" in desc_lower:
        return "low_cards_spread"
    
    return None


def get_all_patterns() -> Dict[str, StrategyAdvice]:
    """Get all available strategic patterns."""
    return BASIC_PATTERNS


def get_strategic_principles() -> Dict[str, str]:
    """Get all strategic principles."""
    return STRATEGIC_PRINCIPLES


def get_royalty_table() -> Dict[str, Dict]:
    """Get royalty point tables."""
    return ROYALTY_POINTS


def format_pattern_advice(advice: StrategyAdvice) -> str:
    """Format strategic advice as a readable string."""
    return f"""
## {advice.pattern}

**Optimal Distribution:** {advice.distribution}

**Reasoning:**
{advice.reasoning}

**Examples:**
{chr(10).join(f"  - {ex}" for ex in advice.examples)}

**Royalty Potential:** {advice.royalty_potential}
**Foul Risk:** {advice.foul_risk}
"""


def format_all_patterns() -> str:
    """Format all patterns as a comprehensive guide."""
    sections = []
    
    sections.append("# OFC Strategic Pattern Guide\n")
    
    for key, advice in BASIC_PATTERNS.items():
        sections.append(format_pattern_advice(advice))
    
    sections.append("\n# Strategic Principles\n")
    for principle, content in STRATEGIC_PRINCIPLES.items():
        sections.append(f"## {principle.replace('_', ' ').title()}\n{content}\n")
    
    return "\n".join(sections)


if __name__ == "__main__":
    # Demo: Show all patterns
    print(format_all_patterns())
