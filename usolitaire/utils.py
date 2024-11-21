# -*- coding: utf-8 -*-

from .deck import Deck
from typing import Literal
from .card import Rank, Suit

def suit_color(suit: Literal["diamonds", "hearts", "clubs", "spades"]) -> Literal["red", "black"]:
    return "red" if suit in ("diamonds", "hearts") else "black"

def rank_diff(first: Rank, second: Rank) -> int:
    """Return the relative difference between the given ranks"""
    assert first in Deck.ranks and second in Deck.ranks
    return Deck.ranks.index(second) - Deck.ranks.index(first)
