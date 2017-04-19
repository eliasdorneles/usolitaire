# -*- coding: utf-8 -*-

import random
from collections import namedtuple


SUIT_SYMBOLS = {
    'spades': u'♠',
    'diamonds': u'♦',
    'clubs': u'♣',
    'hearts': u'♥',
}


class InvalidMove(Exception):
    """Raised to indicate an invalid move"""


class Card(object):
    def __init__(self, rank, suit, face_up=False):
        self.rank = rank
        self.suit = suit
        self.face_up = face_up

    def __repr__(self):
        return 'Card(rank={0.rank!r}, suit={0.suit!r}, face_up={0.face_up!r})'.format(self)

    @property
    def suit_symbol(self):
        return SUIT_SYMBOLS[self.suit]


class Deck(object):
    ranks = [str(n) for n in range(2, 11)] + list('JQKA')
    suits = 'spades diamonds clubs hearts'.split()

    def __init__(self):
        self._cards = [Card(rank, suit)
                       for suit in self.suits
                       for rank in self.ranks]

    def __len__(self):
        return len(self._cards)

    def __getitem__(self, position):
        return self._cards[position]

    def __iter__(self):
        return iter(self._cards)

    def shuffle(self):
        random.shuffle(self._cards)


class Game(object):
    def __init__(self):
        deck = Deck()
        deck.shuffle()
        cards = list(deck)
        self.waste = []
        self.tableau = []
        for n in range(1, 8):
            self.tableau.append([cards.pop() for _ in range(n)])
        for pile in self.tableau:
            pile[-1].face_up = True
        self.stock = list(cards)
        self.foundations = [[], [], [], []]

    def deal_from_stock(self):
        if not self.stock:
            raise InvalidMove("No cards in stock")
        self.waste.append(self.stock.pop())

    def move_pile(self, source_pile, target_pile):
        assert source_pile in range(1, 8) and target_pile in range(1, 8)
