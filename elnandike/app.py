#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urwid
import random
from .game import Deck
from .ui import CardWidget, PALETTE


def exit_on_q(key):
    if key in ('q', 'Q', 'esc'):
        raise urwid.ExitMainLoop()


def main():
    cards = [CardWidget(d) for d in random.sample(list(Deck()), 7)]
    cards[0].turned = True
    cards[3].turned = True
    columns = urwid.Columns(cards)
    loop = urwid.MainLoop(urwid.Filler(columns), PALETTE, unhandled_input=exit_on_q)
    loop.run()


if __name__ == '__main__':
    main()
