from poker.constants import NUM_REGULAR_CARDS, CARD_JOKER, NUM_RANKS
from poker.ofc.constants import MAX_NUM_PLAYERS
from poker.parsing import parse_hand
from poker.card import card_value


def get_n_extra_players(num_players):
    if num_players > MAX_NUM_PLAYERS:
        return num_players - MAX_NUM_PLAYERS
    return 0


def generate_deck(num_players, num_jokers):
    result = list(range(NUM_REGULAR_CARDS))

    n_extra_players = get_n_extra_players(num_players)
    result.extend([
        card_value(rank, suit)
        for suit in range(n_extra_players)
        for rank in range(NUM_RANKS)
    ])

    result.extend([CARD_JOKER] * num_jokers)

    return result


def parse_hands(solution):
    return [parse_hand(x) for x in solution.split('-')]


def flatten_hands(hands):
    return [card for hand in hands for card in hand]


def parse_and_flatten_hands(solution):
    return flatten_hands(parse_hands(solution))
