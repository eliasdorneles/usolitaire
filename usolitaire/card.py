# -*- coding: utf-8 -*-

SUIT_SYMBOLS = {
    "spades": "♠",
    "diamonds": "♦",
    "clubs": "♣",
    "hearts": "♥",
}

class Card(object):
    def __init__(self, rank: str, suit: str, face_up: bool = False):
        self.rank: str = rank
        self.suit: str = suit
        self.face_up: bool = face_up

    def __repr__(self):
        return "Card(rank={0.rank!r}, suit={0.suit!r}, face_up={0.face_up!r})".format(self)

    @property
    def suit_symbol(self):
        return SUIT_SYMBOLS[self.suit]

    @property
    def color(self):
        return "red" if self.suit in ("diamonds", "hearts") else "black"
