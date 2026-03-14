"""Hand input parser for OFC poker hands."""

import re
from typing import Optional
from dataclasses import dataclass


# Card mappings
RANKS = {'A': 'A', 'K': 'K', 'Q': 'Q', 'J': 'J', 'T': 'T', '10': 'T',
         '9': '9', '8': '8', '7': '7', '6': '6', '5': '5', '4': '4', 
         '3': '3', '2': '2'}

SUITS = {'h': 'h', 'H': 'h', '♥': 'h', 'hearts': 'h',
         'd': 'd', 'D': 'd', '♦': 'd', 'diamonds': 'd',
         'c': 'c', 'C': 'c', '♣': 'c', 'clubs': 'c',
         's': 's', 'S': 's', '♠': 's', 'spades': 's'}

SUIT_SYMBOLS = {'h': '♥', 'd': '♦', 'c': '♣', 's': '♠'}
SUIT_COLORS = {'h': 'red', 'd': 'red', 'c': 'black', 's': 'black'}


@dataclass
class Card:
    rank: str
    suit: str
    is_joker: bool = False
    
    def __str__(self):
        if self.is_joker:
            return f"*{self.rank}{self.suit}"
        return f"{self.rank}{self.suit}"
    
    def display(self) -> str:
        """Return display string with suit symbol."""
        symbol = SUIT_SYMBOLS.get(self.suit, self.suit)
        if self.is_joker:
            return f"*{self.rank}{symbol}"
        return f"{self.rank}{symbol}"


@dataclass 
class OFCHand:
    top: list[Card]      # 3 cards
    middle: list[Card]   # 5 cards
    bottom: list[Card]   # 5 cards
    
    def to_solution_format(self) -> str:
        """Convert to database solution format: Top-Middle-Bottom"""
        top_str = "".join(str(c) for c in self.top)
        mid_str = "".join(str(c) for c in self.middle)
        bot_str = "".join(str(c) for c in self.bottom)
        return f"{top_str}-{mid_str}-{bot_str}"
    
    def display(self) -> str:
        """Return formatted display of the hand."""
        top_str = " ".join(c.display() for c in self.top)
        mid_str = " ".join(c.display() for c in self.middle)
        bot_str = " ".join(c.display() for c in self.bottom)
        return f"Top:    {top_str}\nMiddle: {mid_str}\nBottom: {bot_str}"


def parse_card(card_str: str) -> Optional[Card]:
    """
    Parse a single card string.
    
    Accepts formats:
    - Ah, AH, A♥ (Ace of hearts)
    - 10s, Ts, T♠ (Ten of spades)
    - *Kd (Joker as King of diamonds)
    """
    card_str = card_str.strip()
    if not card_str:
        return None
    
    is_joker = card_str.startswith('*')
    if is_joker:
        card_str = card_str[1:]
    
    if len(card_str) < 2:
        return None
    
    # Handle 10 as rank
    if card_str.startswith('10'):
        rank = 'T'
        suit_char = card_str[2:]
    else:
        rank = card_str[0].upper()
        suit_char = card_str[1:]
    
    # Normalize rank
    if rank not in RANKS.values():
        rank = RANKS.get(rank)
        if not rank:
            return None
    
    # Normalize suit
    suit = SUITS.get(suit_char) or SUITS.get(suit_char.lower())
    if not suit:
        return None
    
    return Card(rank=rank, suit=suit, is_joker=is_joker)


def parse_cards(cards_str: str) -> list[Card]:
    """
    Parse a string containing multiple cards.
    
    Accepts formats:
    - "Ah Kd Qs" (space separated)
    - "Ah,Kd,Qs" (comma separated)
    - "AhKdQs" (concatenated - 2 chars each)
    - "Ah-Kd-Qs" (dash separated)
    """
    cards_str = cards_str.strip()
    if not cards_str:
        return []
    
    # Try different separators
    for sep in [' ', ',', '-']:
        if sep in cards_str:
            parts = [p.strip() for p in cards_str.split(sep) if p.strip()]
            cards = [parse_card(p) for p in parts]
            cards = [c for c in cards if c is not None]
            if cards:
                return cards
    
    # Try parsing as concatenated cards (handle jokers with *)
    cards = []
    i = 0
    while i < len(cards_str):
        # Check for joker
        is_joker = cards_str[i] == '*'
        if is_joker:
            i += 1
            if i >= len(cards_str):
                break
        
        # Get rank (handle 10)
        if cards_str[i:i+2] == '10':
            rank = 'T'
            i += 2
        else:
            rank = cards_str[i].upper()
            i += 1
        
        # Get suit
        if i >= len(cards_str):
            break
        suit_char = cards_str[i]
        i += 1
        
        card = parse_card(('*' if is_joker else '') + rank + suit_char)
        if card:
            cards.append(card)
    
    return cards


def parse_ofc_hand(hand_str: str) -> Optional[OFCHand]:
    """
    Parse a full OFC hand in various formats.
    
    Accepts:
    - "AhKdQs-JcTc9c8c7c-6s6h6d5s5h" (solution format)
    - "top: AhKdQs, middle: JcTc9c8c7c, bottom: 6s6h6d5s5h"
    - Partial hands (will fill with None)
    """
    hand_str = hand_str.strip()
    
    # Check for solution format (Top-Middle-Bottom)
    if hand_str.count('-') == 2:
        parts = hand_str.split('-')
        top = parse_cards(parts[0])
        middle = parse_cards(parts[1])
        bottom = parse_cards(parts[2])
        
        if len(top) == 3 and len(middle) == 5 and len(bottom) == 5:
            return OFCHand(top=top, middle=middle, bottom=bottom)
    
    # Check for labeled format
    top_match = re.search(r'top[:\s]+([^\,\n]+)', hand_str, re.IGNORECASE)
    mid_match = re.search(r'mid(?:dle)?[:\s]+([^\,\n]+)', hand_str, re.IGNORECASE)
    bot_match = re.search(r'bot(?:tom)?[:\s]+([^\,\n]+)', hand_str, re.IGNORECASE)
    
    if top_match or mid_match or bot_match:
        top = parse_cards(top_match.group(1)) if top_match else []
        middle = parse_cards(mid_match.group(1)) if mid_match else []
        bottom = parse_cards(bot_match.group(1)) if bot_match else []
        return OFCHand(top=top, middle=middle, bottom=bottom)
    
    return None


def parse_any_cards(text: str) -> list[Card]:
    """
    Extract any cards mentioned in text.
    Useful for finding cards in natural language.
    """
    # Pattern to match cards (with optional joker prefix)
    pattern = r'\*?(?:10|[AKQJT2-9])(?:[hdcs♥♦♣♠])'
    matches = re.findall(pattern, text, re.IGNORECASE)
    
    cards = []
    for match in matches:
        card = parse_card(match)
        if card:
            cards.append(card)
    
    return cards


# Hand type detection
def detect_hand_type(cards: list[Card]) -> str:
    """Detect the poker hand type for a set of cards."""
    if len(cards) < 3:
        return "Unknown"
    
    ranks = [c.rank for c in cards]
    suits = [c.suit for c in cards]
    
    # Count ranks
    rank_counts = {}
    for r in ranks:
        rank_counts[r] = rank_counts.get(r, 0) + 1
    
    counts = sorted(rank_counts.values(), reverse=True)
    is_flush = len(set(suits)) == 1
    
    # Check for straight
    rank_order = "A23456789TJQKA"  # A can be low or high
    rank_indices = sorted(set(rank_order.index(r) for r in ranks if r in rank_order))
    is_straight = False
    if len(rank_indices) == len(cards):
        if rank_indices[-1] - rank_indices[0] == len(cards) - 1:
            is_straight = True
        # Check wheel (A-2-3-4-5)
        if set(ranks) >= {'A', '2', '3', '4', '5'}:
            is_straight = True
    
    # Determine hand type
    if len(cards) == 3:
        if counts[0] == 3:
            return "Trips"
        elif counts[0] == 2:
            return "Pair"
        else:
            return "High Card"
    
    elif len(cards) == 5:
        if counts[0] == 5:
            return "Five of a Kind"
        elif counts[0] == 4:
            return "Four of a Kind"
        elif counts == [3, 2]:
            return "Full House"
        elif is_flush and is_straight:
            if set(ranks) >= {'T', 'J', 'Q', 'K', 'A'}:
                return "Royal Flush"
            return "Straight Flush"
        elif is_flush:
            return "Flush"
        elif is_straight:
            return "Straight"
        elif counts[0] == 3:
            return "Three of a Kind"
        elif counts == [2, 2, 1]:
            return "Two Pair"
        elif counts[0] == 2:
            return "Pair"
        else:
            return "High Card"
    
    return "Unknown"
