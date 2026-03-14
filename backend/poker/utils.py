from .card import Card


def card_values_to_str(values, separator=''):
    return separator.join([str(Card(value)) for value in values])
