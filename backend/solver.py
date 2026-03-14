"""OFC Solver wrapper - interfaces with the C++ CFR solver."""

import numpy as np
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
import framework
from common.combinatorics import generate_ways_to_assign_balls_to_tight_boxes
from poker.ofc.constants import NUM_HOLE_CARDS, HAND_SIZES
from poker.ofc.utils import generate_deck, parse_hands, flatten_hands
from poker.parsing import parse_hand
from poker.constants import CARD_JOKER, RANKS, SUITS, NUM_SUITS
from poker.card import Card


# Pre-compute all possible actions (ways to arrange 13 cards into 3-5-5)
ACTIONS = list(generate_ways_to_assign_balls_to_tight_boxes(NUM_HOLE_CARDS, HAND_SIZES))
NUM_ACTIONS = len(ACTIONS)  # Should be 72072


# Game versions from the database
GAME_VERSIONS = {
    1: {"name": "Original (4p, 4j, 4dc)", "players": 4, "jokers": 4, "dead": 4, "rewarder": 1},
    2: {"name": "Joker Royalties (4p, 4j, 4dc)", "players": 4, "jokers": 4, "dead": 4, "rewarder": 2},
    3: {"name": "Original (4p, 0j, 0dc)", "players": 4, "jokers": 0, "dead": 0, "rewarder": 1},
    4: {"name": "Joker Royalties (3p, 4j, 4dc)", "players": 3, "jokers": 4, "dead": 4, "rewarder": 2},
    5: {"name": "Joker Royalties (3p, 4j, 5dc)", "players": 3, "jokers": 4, "dead": 5, "rewarder": 2},
    6: {"name": "Joker Royalties (3p, 4j, 6dc)", "players": 3, "jokers": 4, "dead": 6, "rewarder": 2},
    7: {"name": "Joker Royalties (2p, 4j, 4dc)", "players": 2, "jokers": 4, "dead": 4, "rewarder": 2},
}

# Default solving parameters
# Upgraded to Railway Pro - high accuracy config
DEFAULT_ITERATIONS = 1000
DEFAULT_TRAVERSALS = 10


@dataclass
class SolverResult:
    """Result from solving an OFC hand."""
    solution: str  # Best solution in "Top-Middle-Bottom" format
    ev: float  # Expected value
    frequency: float  # GTO frequency for this play
    alternatives: List[Dict[str, Any]]  # Alternative plays with EVs and frequencies
    hole_cards: str  # Original hole cards
    dead_cards: str  # Dead cards used
    game_version: int
    iterations: int
    traversals: int


def card_to_string(card_value: int) -> str:
    """Convert card value to string notation (e.g., 48 -> 'Ah')."""
    if card_value == CARD_JOKER:
        return "*"
    rank = card_value // NUM_SUITS
    suit = card_value % NUM_SUITS
    return RANKS[rank] + SUITS[suit]


def cards_to_string(cards: List[int]) -> str:
    """Convert list of card values to string."""
    return "".join(card_to_string(c) for c in cards)


def hand_to_string(cards: List[int], action_indices: Tuple[int, ...]) -> str:
    """Convert card indices using an action to a hand string."""
    return "".join(card_to_string(cards[i]) for i in action_indices)


def action_to_solution(cards: List[int], action_index: int) -> str:
    """Convert an action index to a solution string."""
    action = ACTIONS[action_index]
    top = hand_to_string(cards, action[0])
    middle = hand_to_string(cards, action[1])
    bottom = hand_to_string(cards, action[2])
    return f"{top}-{middle}-{bottom}"


def parse_cards_string(cards_str: str) -> List[int]:
    """Parse a card string like 'Ah Kd Qc...' into card values."""
    return parse_hand(cards_str)


class OFCSolver:
    """High-level wrapper for the C++ OFC solver."""
    
    def __init__(self):
        self.evaluator = framework.OFCEvaluator()
    
    def solve(
        self,
        hole_cards: str,
        dead_cards: str = "",
        game_version: int = 2,
        iterations: int = DEFAULT_ITERATIONS,
        traversals: int = DEFAULT_TRAVERSALS,
        top_n: int = 5
    ) -> SolverResult:
        """
        Solve an OFC hand using CFR.
        
        Args:
            hole_cards: 13 cards as string (e.g., "Ah Kd Qc Js Th 9h 8h 7h 6h 5h 4h 3h 2h")
            dead_cards: Dead cards as string (e.g., "5s Kh 9c Tc")
            game_version: Game variant (1-7), default 2 (Joker Royalties 4p)
            iterations: Number of CFR iterations (more = better but slower)
            traversals: Number of traversals per iteration
            top_n: Number of top alternatives to return
            
        Returns:
            SolverResult with best play and alternatives
        """
        # Get game config
        game = GAME_VERSIONS.get(game_version)
        if not game:
            raise ValueError(f"Unknown game version: {game_version}")
        
        # Parse cards
        hole_list = parse_cards_string(hole_cards)
        dead_list = parse_cards_string(dead_cards) if dead_cards else []
        
        # Validate
        if len(hole_list) != NUM_HOLE_CARDS:
            raise ValueError(f"Expected {NUM_HOLE_CARDS} hole cards, got {len(hole_list)}")
        
        expected_dead = game["dead"]
        if len(dead_list) != expected_dead:
            raise ValueError(f"Game version {game_version} expects {expected_dead} dead cards, got {len(dead_list)}")
        
        # Create solver
        solver = framework.OFCSolver.create(
            game["players"],
            game["jokers"],
            game["dead"],
            game["rewarder"]
        )
        
        # Run CFR
        frequencies = solver.solve(hole_list, dead_list, iterations, traversals)
        
        # Normalize frequencies to sum to 1.0 (CFR returns unnormalized strategy weights)
        freq_sum = np.sum(frequencies)
        if freq_sum > 0:
            frequencies = frequencies / freq_sum
        
        # Get top actions by frequency
        top_indices = np.argsort(frequencies)[-top_n:][::-1]
        
        # Build results
        best_idx = int(top_indices[0])
        best_solution = action_to_solution(hole_list, best_idx)
        best_ev = solver.get_ev(best_idx)
        best_freq = float(frequencies[best_idx])
        
        alternatives = []
        for idx in top_indices:
            idx = int(idx)
            sol = action_to_solution(hole_list, idx)
            ev = solver.get_ev(idx)
            freq = float(frequencies[idx])
            
            # Get hand types using evaluator
            action = ACTIONS[idx]
            top_cards = [hole_list[i] for i in action[0]]
            mid_cards = [hole_list[i] for i in action[1]]
            bot_cards = [hole_list[i] for i in action[2]]
            
            # Get hand types
            from hand_parser import Card, detect_hand_type
            
            def to_card(c):
                """Convert card value to Card object."""
                if c == CARD_JOKER:
                    return Card(rank='*', suit='*', is_joker=True)
                card_str = card_to_string(c)
                return Card(rank=card_str[0], suit=card_str[1], is_joker=False)
            
            top_parsed = [to_card(c) for c in top_cards]
            mid_parsed = [to_card(c) for c in mid_cards]
            bot_parsed = [to_card(c) for c in bot_cards]
            
            alternatives.append({
                "solution": sol,
                "ev": round(ev, 4),
                "frequency": round(freq * 100, 4),  # As percentage
                "top": {
                    "cards": cards_to_string(top_cards),
                    "hand_type": detect_hand_type(top_parsed)
                },
                "middle": {
                    "cards": cards_to_string(mid_cards),
                    "hand_type": detect_hand_type(mid_parsed)
                },
                "bottom": {
                    "cards": cards_to_string(bot_cards),
                    "hand_type": detect_hand_type(bot_parsed)
                },
            })
        
        return SolverResult(
            solution=best_solution,
            ev=round(best_ev, 4),
            frequency=round(best_freq * 100, 4),
            alternatives=alternatives,
            hole_cards=hole_cards,
            dead_cards=dead_cards,
            game_version=game_version,
            iterations=iterations,
            traversals=traversals
        )
    
    def evaluate_solution(
        self,
        solution: str,
        dead_cards: str = "",
        game_version: int = 2,
        iterations: int = DEFAULT_ITERATIONS,
        traversals: int = DEFAULT_TRAVERSALS
    ) -> Dict[str, Any]:
        """
        Evaluate a specific solution's EV against GTO.
        
        Args:
            solution: Solution string like "Ah4s3h-As5c4c3c2h-KdJd9d7d3d"
            dead_cards: Dead cards
            game_version: Game variant
            iterations: CFR iterations
            traversals: Traversals per iteration
            
        Returns:
            Dict with solution EV and comparison to GTO best play
        """
        # Parse the solution to get hole cards
        hands = parse_hands(solution)
        hole_list = flatten_hands(hands)
        hole_str = " ".join(card_to_string(c) for c in hole_list)
        
        # Solve to get GTO
        gto_result = self.solve(
            hole_str,
            dead_cards,
            game_version,
            iterations,
            traversals
        )
        
        # Find the given solution in actions
        target_top = tuple(sorted(range(3)))  # We need to map the actual cards
        
        # For now, compute EV directly
        game = GAME_VERSIONS[game_version]
        dead_list = parse_cards_string(dead_cards) if dead_cards else []
        
        solver = framework.OFCSolver.create(
            game["players"],
            game["jokers"],
            game["dead"],
            game["rewarder"]
        )
        
        frequencies = solver.solve(hole_list, dead_list, iterations, traversals)
        
        # Find the action that matches the given solution
        given_top = set(range(3))  # Cards 0-2 in the solution are top
        given_mid = set(range(3, 8))  # Cards 3-7 are middle
        given_bot = set(range(8, 13))  # Cards 8-12 are bottom
        
        # Find matching action index
        found_idx = None
        for i, action in enumerate(ACTIONS):
            if (set(action[0]) == given_top and 
                set(action[1]) == given_mid and 
                set(action[2]) == given_bot):
                found_idx = i
                break
        
        if found_idx is None:
            # The solution order doesn't match standard indexing, compute EV differently
            # Use the evaluator to get strengths and compute approximate EV
            strengths = self.evaluator.get_strengths(hands)
            return {
                "solution": solution,
                "gto_best": gto_result.solution,
                "gto_ev": gto_result.ev,
                "note": "Could not find exact action match - solution may use different card ordering"
            }
        
        solution_ev = solver.get_ev(found_idx)
        solution_freq = float(frequencies[found_idx])
        
        return {
            "solution": solution,
            "ev": round(solution_ev, 4),
            "frequency": round(solution_freq * 100, 4),
            "gto_best": gto_result.solution,
            "gto_ev": gto_result.ev,
            "gto_frequency": gto_result.frequency,
            "ev_loss": round(gto_result.ev - solution_ev, 4)
        }


# Singleton instance
_solver = None

def get_solver() -> OFCSolver:
    """Get the singleton solver instance."""
    global _solver
    if _solver is None:
        _solver = OFCSolver()
    return _solver


def solve_hand(
    hole_cards: str,
    dead_cards: str = "",
    game_version: int = 2,
    iterations: int = DEFAULT_ITERATIONS,
    traversals: int = DEFAULT_TRAVERSALS
) -> SolverResult:
    """Convenience function to solve a hand."""
    return get_solver().solve(hole_cards, dead_cards, game_version, iterations, traversals)


if __name__ == "__main__":
    # Test the solver
    print("Testing OFC Solver...")
    
    # Example hand
    hole = "Ah Kd Qc Js Th 9h 8c 7d 6s 5h 4c 3d 2s"
    dead = "Ac Kh Qd Jc"
    
    print(f"Hole cards: {hole}")
    print(f"Dead cards: {dead}")
    print("Solving...")
    
    result = solve_hand(hole, dead, game_version=2, iterations=1000, traversals=10)
    
    print(f"\nBest solution: {result.solution}")
    print(f"EV: {result.ev}")
    print(f"Frequency: {result.frequency}%")
    print(f"\nTop alternatives:")
    for i, alt in enumerate(result.alternatives, 1):
        print(f"  {i}. {alt['solution']} (EV: {alt['ev']}, Freq: {alt['frequency']}%)")
