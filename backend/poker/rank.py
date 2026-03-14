from .constants import RANKS, NUM_SUITS


class Rank:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return RANKS[self.value]

    def __eq__(self, other):
        if isinstance(other, Rank):
            return self.value == other.value

        elif isinstance(other, int):
            return self.value == other

        return False

    def __hash__(self):
        return hash(self.value)

    @staticmethod
    def from_card(card):
        return Rank(card // NUM_SUITS)
