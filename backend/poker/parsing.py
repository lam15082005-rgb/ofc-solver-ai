from .card import card_value
from .constants import RANKS, SUITS, CARD_JOKER


STR_JOKER = '*'
RANK_LENGTH = 1
SUIT_LENGTH = 1
CARD_LENGTH = 2


def parse_rank(text):
    if len(text) == RANK_LENGTH:
        result = RANKS.find(text)
        if result >= 0:
            return result

    raise ValueError(f"Invalid rank: {text}")


def parse_suit(text):
    if len(text) == SUIT_LENGTH:
        return SUITS.find(text)

    raise ValueError(f"Invalid suit: {text}")


def parse_card(text):
    if len(text) == CARD_LENGTH:
        rank = parse_rank(text[0])
        suit = parse_suit(text[1])
        return card_value(rank, suit)

    raise ValueError(f"Invalid card: {text}")


def parse_hand(text):
    result = []

    i = 0
    while i < len(text):
        if text[i] == ' ':
            i += 1
            continue

        if text[i] == STR_JOKER:
            result.append(CARD_JOKER)
            i += 1
            continue

        if len(text) - i < CARD_LENGTH:
            raise ValueError(f"Invalid hand: {text}")

        card = parse_card(text[i:i + CARD_LENGTH])
        result.append(card)

        i += CARD_LENGTH

    return result
