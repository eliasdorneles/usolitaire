# -*- coding: utf-8 -*-
from typing import Literal

SUIT_SYMBOLS = {
    "spades": "♠",
    "diamonds": "♦",
    "clubs": "♣",
    "hearts": "♥",
}

Rank = Literal["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
Suit = Literal["spades", "diamonds", "clubs", "hearts"]


class Card(object):
    def __init__(self, rank: Rank, suit: Suit, face_up: bool = False):
        self.rank: Rank = rank
        self.suit: Suit = suit
        self.face_up = face_up

    def __repr__(self):
        return "Card(rank={0.rank!r}, suit={0.suit!r}, face_up={0.face_up!r})".format(self)

    @property
    def suit_symbol(self):
        return SUIT_SYMBOLS[self.suit]

    @property
    def color(self):
        return "red" if self.suit in ("diamonds", "hearts") else "black"
