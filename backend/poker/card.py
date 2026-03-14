from .constants import NUM_SUITS, CARD_JOKER, CARD_NONE
from .rank import Rank
from .suit import Suit


def card_value(rank, suit):
    return rank * NUM_SUITS + suit


class Card:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        if self.value == CARD_JOKER:
            return '*'

        if self.value == CARD_NONE:
            return '-'

        return str(Rank.from_card(self.value)) + str(Suit.from_card(self.value))
