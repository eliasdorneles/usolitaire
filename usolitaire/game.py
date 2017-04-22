# -*- coding: utf-8 -*-

import random


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
    ranks = ['A'] + [str(n) for n in range(2, 11)] + list('JQK')
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


def suit_color(suit):
    return 'red' if suit in ('diamonds', 'hearts') else 'black'


def rank_diff(first, second):
    """Return the relative difference between the given ranks"""
    assert first in Deck.ranks and second in Deck.ranks
    return Deck.ranks.index(second) - Deck.ranks.index(first)


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
        self.waste[-1].face_up = True

    def restore_stock(self):
        self.stock = list(reversed(self.waste))
        for card in self.stock:
            card.face_up = False
        self.waste[:] = []

    def _is_valid_move_to_tableau(self, source_card, target_card):
        if target_card is None:
            return source_card.rank == 'K'
        if not source_card.face_up or not target_card.face_up:
            return False
        diff = rank_diff(source_card.rank, target_card.rank)
        return diff == 1 and suit_color(source_card.suit) != suit_color(target_card.suit)

    def move_from_waste_to_tableau(self, target_index):
        assert target_index in range(7)
        target_pile = self.tableau[target_index]
        target_card = target_pile[-1] if target_pile else None
        if self.waste and self._is_valid_move_to_tableau(self.waste[-1], target_card):
            target_pile.append(self.waste.pop())
        else:
            raise InvalidMove()

    def move_tableau_pile(self, src_index, target_index):
        """Move pile, assuming that cards facing up are in the proper order"""
        assert src_index in range(7), "Invalid index: %r" % src_index
        assert target_index in range(7), "Invalid index: %r" % target_index
        if src_index == target_index:
            raise InvalidMove('Source is same as destination')
        source_pile, target_pile = self.tableau[src_index], self.tableau[target_index]
        target_card = target_pile[-1] if target_pile else None
        for index, card in list(enumerate(source_pile))[::-1]:
            if self._is_valid_move_to_tableau(card, target_card):
                to_move = source_pile[index:]
                target_pile.extend(to_move)
                for _ in range(len(to_move)):
                    source_pile.pop()
                return
        raise InvalidMove()

    def _find_foundation_pile(self, card_to_move):
        for pile in self.foundations:
            if any([
                    not pile and card_to_move.rank == 'A',
                    pile and card_to_move.suit == pile[-1].suit and
                    rank_diff(card_to_move.rank, pile[-1].rank) == -1
            ]):
                return pile

    def move_to_foundation_from_waste(self):
        if not self.waste:
            raise InvalidMove()
        foundation_pile = self._find_foundation_pile(self.waste[-1])
        if foundation_pile is None:
            raise InvalidMove()
        foundation_pile.append(self.waste.pop())

    def move_to_foundation_from_tableau(self, index):
        assert index in range(7), "Invalid index: %r" % index
        pile = self.tableau[index]
        if not pile:
            raise InvalidMove()
        card_to_move = pile[-1]
        if not card_to_move.face_up:
            raise InvalidMove()

        foundation_pile = self._find_foundation_pile(card_to_move)
        if foundation_pile is None:
            raise InvalidMove()
        foundation_pile.append(pile.pop())
