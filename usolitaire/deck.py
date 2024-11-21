# -*- coding: utf-8 -*-

import random
from .card import Card, Rank, Suit

class Deck(object):
    ranks: list[Rank] = ["A"] + [str(n) for n in range(2, 11)] + list("JQK")  # type: ignore
    suits = "spades diamonds clubs hearts".split()

    def __init__(self):
        self._cards = [Card(rank, suit) for suit in self.suits for rank in self.ranks]

    def __len__(self):
        return len(self._cards)

    def __getitem__(self, position):
        return self._cards[position]

    def __iter__(self):
        return iter(self._cards)

    def shuffle(self):
        random.shuffle(self._cards)
