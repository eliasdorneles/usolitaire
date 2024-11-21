# -*- coding: utf-8 -*-

from .deck import Deck

def suit_color(suit):
    return "red" if suit in ("diamonds", "hearts") else "black"

def rank_diff(first, second):
    """Return the relative difference between the given ranks"""
    assert first in Deck.ranks and second in Deck.ranks
    return Deck.ranks.index(second) - Deck.ranks.index(first)
