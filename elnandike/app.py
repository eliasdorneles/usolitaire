#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
import urwid
from .game import Deck
from .ui import CardWidget, CardPileWidget, PALETTE


def exit_on_q(key):
    if key in ('q', 'Q', 'esc'):
        raise urwid.ExitMainLoop()


def main(args):
    deck = Deck()
    deck.shuffle()
    cards = [CardWidget(d) for d in deck[:7]]
    cards[0].face_up = False
    cards[3].face_up = False
    for c in cards[:4]:
        c.playable = True

    main_layout = urwid.Pile([
        urwid.Columns(cards),
        urwid.Divider(),
        urwid.Columns([CardPileWidget(deck[:i]) for i in range(1, 8)]),
    ])

    if args.shell:
        from IPython import embed
        embed()
    else:
        loop = urwid.MainLoop(
            urwid.Filler(main_layout, valign='top'),
            PALETTE,
            unhandled_input=exit_on_q,
        )
        loop.run()


if '__main__' == __name__:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--shell', action='store_true')

    args = parser.parse_args()
    main(args)
