from .constants import SUITS, NUM_SUITS


class Suit:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return SUITS[self.value]

    @staticmethod
    def from_card(card):
        return Suit(card % NUM_SUITS)
