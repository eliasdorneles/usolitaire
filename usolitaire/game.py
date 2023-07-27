# -*- coding: utf-8 -*-

import random

SUIT_SYMBOLS = {
    "spades": "♠",
    "diamonds": "♦",
    "clubs": "♣",
    "hearts": "♥",
}


class InvalidMove(Exception):
    """Raised to indicate an invalid move"""


class Card(object):
    def __init__(self, rank, suit, face_up=False):
        self.rank = rank
        self.suit = suit
        self.face_up = face_up

    def __repr__(self):
        return "Card(rank={0.rank!r}, suit={0.suit!r}, face_up={0.face_up!r})".format(self)

    @property
    def suit_symbol(self):
        return SUIT_SYMBOLS[self.suit]

    @property
    def color(self):
        return "red" if self.suit in ("diamonds", "hearts") else "black"


class Deck(object):
    ranks = ["A"] + [str(n) for n in range(2, 11)] + list("JQK")
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


def suit_color(suit):
    return "red" if suit in ("diamonds", "hearts") else "black"


def rank_diff(first, second):
    """Return the relative difference between the given ranks"""
    assert first in Deck.ranks and second in Deck.ranks
    return Deck.ranks.index(second) - Deck.ranks.index(first)


class Game(object):
    """
    Class implementing the game logic.

    The game is played with a standard deck of 52 cards.

    The cards are dealt into 7 piles, with the first pile containing one card,
    the second pile containing two cards, and so on.
    The top card of each pile is face up; all others are face down.
    The remaining cards are placed face down to form the stock.

    How to use:
    >>> game = Game()
    >>> game.deal_from_stock()
    >>> game.move_from_waste_to_tableau(0)
    >>> game.move_tableau_pile(0, 1) # moving a pile
    >>> game.move_tableau_pile(1, 2) # moving another pile
    >>> game.move_from_waste_to_tableau(0)
    """

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

    def _reset_game_to_almost_won_state(self):
        """
        Reset the game to a state where only one move is needed to win.
        Never used in actual game, it exists just to facilicate testing winning.
        """
        deck = Deck()
        cards = list(deck)
        for c in cards:
            c.face_up = True
        self.waste = []
        self.tableau = []
        for n in range(1, 8):
            self.tableau.append([])
        self.foundations = [
            cards[0:13],
            cards[13 : 13 * 2],
            cards[13 * 2 : 13 * 3],
            cards[13 * 3 : 13 * 4 - 1],
        ]
        self.stock = []
        self.waste = [cards[-1]]

    def deal_from_stock(self):
        """Deal one card from stock to waste"""
        if not self.stock:
            raise InvalidMove("No cards in stock")
        self.waste.append(self.stock.pop())
        self.waste[-1].face_up = True

    def restore_stock(self):
        """Restore stock from waste"""
        self.stock[:] = list(reversed(self.waste))
        for card in self.stock:
            card.face_up = False
        self.waste[:] = []

    def _is_valid_move_to_tableau(self, source_card, target_card):
        """Check if the given card can be moved to the given tableau pile"""
        if target_card is None:
            return source_card.rank == "K"
        if not source_card.face_up or not target_card.face_up:
            return False
        diff = rank_diff(source_card.rank, target_card.rank)
        return diff == 1 and suit_color(source_card.suit) != suit_color(target_card.suit)

    def can_move_card_to_tableau(self, card, tableau_index):
        """Check if the given card can be moved to the given tableau pile"""
        assert tableau_index in range(7)
        target_pile = self.tableau[tableau_index]
        target_card = target_pile[-1] if target_pile else None
        return self._is_valid_move_to_tableau(card, target_card)

    def move_from_waste_to_tableau(self, target_index):
        """Move card from waste to tableau"""
        assert target_index in range(7)
        target_pile = self.tableau[target_index]
        target_card = target_pile[-1] if target_pile else None
        if self.waste and self._is_valid_move_to_tableau(self.waste[-1], target_card):
            target_pile.append(self.waste.pop())
        else:
            raise InvalidMove()

    def can_move_from_waste_to_tableau(self, tableau_index):
        """Check if card from waste can be moved to tableau"""
        if self.waste:
            return self.can_move_card_to_tableau(self.waste[-1], tableau_index)
        return False

    def move_tableau_pile(self, src_index, target_index):
        """
        Move pile, assuming that cards facing up are in the proper order
        and that the target pile is empty or the top card is facing up.
        """
        assert src_index in range(7), "Invalid index: %r" % src_index
        assert target_index in range(7), "Invalid index: %r" % target_index
        if src_index == target_index:
            raise InvalidMove("Source is same as destination")
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
        """Find a foundation pile where the given card can be moved"""
        for pile in self.foundations:
            if any(
                [
                    not pile and card_to_move.rank == "A",
                    pile
                    and card_to_move.suit == pile[-1].suit
                    and rank_diff(card_to_move.rank, pile[-1].rank) == -1,
                ]
            ):
                return pile

    def move_to_foundation_from_waste(self):
        """
        Move card from waste to foundation.
        Card must be facing up and must be the next card in the foundation pile.
        """
        if not self.waste:
            raise InvalidMove()
        foundation_pile = self._find_foundation_pile(self.waste[-1])
        if foundation_pile is None:
            raise InvalidMove()
        foundation_pile.append(self.waste.pop())

    def can_move_to_foundation_from_waste(self) -> bool:
        """
        Check if the top card of the waste can be moved to foundation
        """
        if not self.waste:
            return False
        foundation_pile = self._find_foundation_pile(self.waste[-1])
        return foundation_pile is not None

    def move_to_foundation_from_tableau(self, index):
        """
        Move card from tableau to foundation.
        Card must be facing up and must be the next card in the foundation pile.
        """
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

    def can_move_to_foundation_from_tableau(self, index) -> bool:
        """
        Check if the top card of the given tableau pile can be moved to foundation
        """
        assert index in range(7), "Invalid index: %r" % index
        pile = self.tableau[index]
        if not pile:
            return False
        card_to_move = pile[-1]
        if not card_to_move.face_up:
            return False
        foundation_pile = self._find_foundation_pile(card_to_move)
        return foundation_pile is not None

    def won(self):
        """Check if the game is won"""
        return all(len(pile) == 13 for pile in self.foundations)
