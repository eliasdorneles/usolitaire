# -*- coding: utf-8 -*-

from .deck import Deck
from typing import Literal

def suit_color(suit: Literal["diamonds", "hearts", "clubs", "spades"]) -> Literal["red", "black"]:
    return "red" if suit in ("diamonds", "hearts") else "black"

def rank_diff(first: str, second: str) -> int:
    """Return the relative difference between the given ranks"""
    assert first in Deck.ranks and second in Deck.ranks
    return Deck.ranks.index(second) - Deck.ranks.index(first)
