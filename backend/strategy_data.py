"""Data-driven strategic insights extracted from 327k+ GTO-solved hands.

These insights are derived from actual CFR solver outputs, not human intuition.
Each insight includes the empirical EV data to back it up.
"""

# ============================================================================
# KEY INSIGHT #1: TOP ROW PAIR VALUES
# ============================================================================
# Putting your highest pair on top is ALWAYS correct.
# The EV differences are significant:

TOP_PAIR_EV = {
    "PairOfAces": -1.19,    # BEST - always put AA on top if available
    "PairOfKings": -4.40,   # 3.2 EV worse than AA
    "PairOfQueens": -5.45,  # 1.0 EV worse than KK  
    "PairOfJacks": -7.28,   # 1.8 EV worse than QQ
    "PairOfTens": -7.65,    # 0.4 EV worse than JJ
    "PairOfNines": -8.18,
    "PairOfEights": -8.66,
    "PairOfSevens": -8.99,
    "PairOfSixes": -8.34,
    "PairOfFives": -9.05,
    "PairOfFours": -9.20,
    "PairOfThrees": -10.14,
    "PairOfDeuces": -9.79,
    "HighCard": -5.07,      # High card top is common but not great
    "ThreeOfAKind": 25.16,  # TRIPS ON TOP IS AMAZING!
}

TOP_PAIR_INSIGHT = """
DATA-DRIVEN INSIGHT: Top Row Pair Selection

From 327k solved hands, the EV by top pair:
- AA on top: -1.19 EV (BEST)
- KK on top: -4.40 EV (3.2 points worse than AA!)
- QQ on top: -5.45 EV 
- JJ on top: -7.28 EV
- TT on top: -7.65 EV

KEY TAKEAWAY: Always put your HIGHEST pair on top.
The 3.2 EV difference between AA and KK is MASSIVE - that's like winning
an extra row every 3 hands on average.

TRIPS ON TOP: +25.16 EV (!!!)
Trips on top is generally very strong (3 pts royalty + high win rate).
But this is a heuristic — always defer to the solver for specific hands.
"""


# ============================================================================
# KEY INSIGHT #2: TRIPS PLACEMENT
# ============================================================================
# Counterintuitive: Trips on TOP is WAY better than trips elsewhere!

TRIPS_PLACEMENT_EV = {
    "Trips on TOP": 25.16,      # BEST BY FAR
    "Trips in MIDDLE": -8.49,   # 33 EV worse!
    "Trips on BOTTOM": -16.58,  # 42 EV worse!
}

TRIPS_INSIGHT = """
DATA-DRIVEN INSIGHT: Trips Placement

Solver data shows trips placement EV:
- Trips on TOP: +25.16 EV (HUGE POSITIVE!)
- Trips in MIDDLE: -8.49 EV
- Trips on BOTTOM: -16.58 EV

DIFFERENCE: ~33-42 EV between top and other placements!

WHY? Trips on top (3 pts royalty) combined with a very high win rate
makes this extremely profitable on average.

However, this is an average heuristic — NOT an absolute rule.
If you can make quads in middle (8 pts!) vs trips in middle (1 pt),
the 7-point royalty swing may outweigh. Always defer to solver.
"""


# ============================================================================
# KEY INSIGHT #3: PREMIUM HANDS - MIDDLE vs BOTTOM (CORRELATION, NOT CAUSATION!)
# ============================================================================
# IMPORTANT: Higher EV for "premium in middle" is because you need SOMETHING
# STRONGER on bottom. It's a correlation with having MULTIPLE premium hands,
# not a strategy to "put flush in middle."

MIDDLE_VS_BOTTOM_EV = {
    "Quads": {
        "middle": 42.83,   # +42.83 EV (means bottom is even stronger!)
        "bottom": 5.86,    # +5.86 EV (quads is your best hand)
        "note": "Quads in middle = you have straight flush or 5oak on bottom",
    },
    "FullHouse": {
        "middle": 10.50,   # +10.5 EV (bottom is quads/SF)
        "bottom": -8.69,   # -8.69 EV (FH is your best hand)
        "note": "FH in middle = you have quads or better on bottom",
    },
    "Flush": {
        "middle": 0.65,    # +0.65 EV (bottom is FH/quads/SF)
        "bottom": -9.72,   # -9.72 EV (flush is your best hand)
        "note": "Flush in middle = you have full house+ on bottom",
    },
    "Straight": {
        "middle": -1.50,   # ~-1.5 EV (bottom is flush+)
        "bottom": -11.00,  # ~-11 EV (straight is your best hand)
        "note": "Straight in middle = you have flush+ on bottom",
    },
}

MIDDLE_VS_BOTTOM_INSIGHT = """
DATA-DRIVEN INSIGHT: Premium Hand Placement (CORRELATION, NOT CAUSATION!)

The data shows higher EV when premium hands are in middle:

                    MIDDLE      BOTTOM      
Quads:              +42.83      +5.86       
Full House:         +10.50      -8.69       
Flush:              +0.65       -9.72       

BUT THIS IS CORRELATION, NOT STRATEGY!

WHY the EV difference? Because middle must be WEAKER than bottom:
- Flush in middle → you have full house/quads/SF on BOTTOM
- So "flush in middle" = "I have TWO premium hands"
- The high EV comes from having multiple premium hands, not placement choice

CORRECT INTERPRETATION:
- If you only have ONE premium hand, it goes on bottom (no choice)
- If you have TWO premium hands, weaker one goes in middle (structure)
- The EV data shows that having multiple premium hands is very profitable

ROYALTY NOTE (actual solver values): Middle quads = 8 pts vs Bottom quads = 4 pts.
Middle full house = 2 pts vs Bottom full house = 1 pt.
These differences matter when you have multiple premium hands.
"""


# ============================================================================
# KEY INSIGHT #4: BOTTOM ROW HAND VALUES
# ============================================================================

BOTTOM_ROW_EV = {
    "FiveOfAKind": 20.41,           # Joker hands - best bottom
    "StraightFlushAceHigh": 12.49,  # Royal flush
    "StraightFlush": 7.50,          # Average SF (varies 5-12)
    "FourOfAKind": 5.86,            # Quads
    "FullHouse": -8.69,             # Negative EV!
    "FlushAceHigh": -8.21,
    "Flush": -9.72,                 # Average flush
    "StraightAceHigh": -10.00,
    "Straight": -11.00,             # Average straight
}

BOTTOM_ROW_INSIGHT = """
DATA-DRIVEN INSIGHT: Bottom Row Expected Values

Only premium hands have POSITIVE EV on bottom:
- Five of a Kind (jokers): +20.41 EV
- Straight Flush: +5 to +12 EV
- Four of a Kind: +5.86 EV

Everything else is NEGATIVE:
- Full House: -8.69 EV
- Flush: -9.72 EV
- Straight: -11 EV

IMPLICATION: Don't chase bottom strength at the expense of
middle/top value. A full house on bottom (-8.69) is worse than
putting those cards in middle (+10.5) if you can make it work!
"""


# ============================================================================
# KEY INSIGHT #5: THE THREE-STRONG-HANDS PRINCIPLE
# ============================================================================

THREE_HANDS_INSIGHT = """
DATA-DRIVEN INSIGHT: Build THREE Strong Hands

Analysis of 327k hands shows that balanced structures outperform
"dump everything in bottom" strategies.

Example with 5 pairs (AA, KK, QQ, 99, 77):

WRONG: KK-9977-AAQQ
- Top: KK (1 pt royalty, wins less often than AA)
- Middle: 9977 (weak - loses often)
- Bottom: AAQQ (very strong)
- Problem: Weak middle loses too many row matchups

RIGHT: AA-QQ99-KK77
- Top: AA (1 pt royalty, wins most often)
- Middle: QQ99 (stronger - wins more often)
- Bottom: KK77 (still wins most matchups)
- Result: Better row win rate overall

The data confirms: Maximize TOP royalties first, then build
balanced middle/bottom rather than one super-strong + one weak.
"""


# ============================================================================
# COMPILED STRATEGIC PRINCIPLES (Data-Backed)
# ============================================================================

DATA_DRIVEN_PRINCIPLES = {
    "top_pair_selection": {
        "rule": "Always put your HIGHEST pair on top",
        "evidence": "AA top = -1.19 EV, KK top = -4.40 EV (3.2 point difference)",
        "exception": "Unless you can make trips on top (+25.16 EV)",
    },
    
    "trips_placement": {
        "rule": "Trips on TOP is generally very strong (heuristic, not absolute)",
        "evidence": "Trips top = +25.16 EV vs middle = -8.49 EV (average across 327k hands)",
        "exception": "When quads in middle (8 pts royalty) is available — always defer to solver",
    },
    
    "premium_hand_placement": {
        "rule": "Put premium hands (flush+) in MIDDLE if structure allows",
        "evidence": "Quads middle +42.83 vs bottom +5.86 (37 point difference!)",
        "rationale": "Middle royalties are 1.5-2x higher than bottom royalties",
    },
    
    "balanced_structure": {
        "rule": "Build three competitive hands, not one super-strong + one weak",
        "evidence": "Balanced two-pair distributions outperform extreme splits",
        "rationale": "Winning 2-3 rows beats winning 1 row with higher margin",
    },
    
    "royalty_priority": {
        "rule": "Maximize total royalties across all three rows",
        "evidence": "Top trips = 3 pts, Middle quads = 8 pts, Bottom quads = 4 pts (actual solver values)",
        "rationale": "Quads in middle (8 pts) is the most valuable non-SF royalty",
    },
}


def get_all_insights():
    """Return all data-driven insights as a formatted string."""
    return "\n\n".join([
        "# DATA-DRIVEN OFC STRATEGY",
        "# Based on analysis of 327,673 GTO-solved hands",
        "",
        TOP_PAIR_INSIGHT,
        TRIPS_INSIGHT,
        MIDDLE_VS_BOTTOM_INSIGHT,
        BOTTOM_ROW_INSIGHT,
        THREE_HANDS_INSIGHT,
    ])


def get_ev_lookup(hand_type: str, position: str) -> float:
    """Get the average EV for a hand type in a given position."""
    if position == "top":
        return TOP_PAIR_EV.get(hand_type, -10.0)
    elif position == "middle":
        if hand_type in MIDDLE_VS_BOTTOM_EV:
            return MIDDLE_VS_BOTTOM_EV[hand_type]["middle"]
    elif position == "bottom":
        return BOTTOM_ROW_EV.get(hand_type, -10.0)
    return None


if __name__ == "__main__":
    print(get_all_insights())
