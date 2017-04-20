#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Console-based Solitaire
"""

from __future__ import print_function, absolute_import, division
import urwid
from .game import Game
from .ui import CardWidget, CardPileWidget, SpacerWidget, EmptyCardWidget, PALETTE


class GameApp(object):
    def __init__(self):
        self.game = Game()
        self._statusbar = urwid.Text(u'Ready')
        self._tableau_columns = urwid.Columns([
            CardPileWidget(pile, onclick=self.pile_card_clicked)
            for pile in self.game.tableau
        ])
        self._top_columns = urwid.Columns([
            CardWidget(self.game.stock[-1]),
            EmptyCardWidget(),
            SpacerWidget(),
            EmptyCardWidget(),
            EmptyCardWidget(),
            EmptyCardWidget(),
            EmptyCardWidget(),
        ])

        self.main_layout = urwid.Pile([
            self._top_columns,
            urwid.Divider(),
            self._tableau_columns,
            urwid.Divider(),
            self._statusbar,
        ])

    def pile_card_clicked(self, card_widget, pile=None):
        if not pile.top.face_up:
            pile.top.face_up = True
            self.update_status('Good job')
        else:
            card = pile.cards.pop()
            pile.redraw()
            self.update_status('Popped: %r' % card)

    def update_status(self, text):
        self._statusbar.set_text(text)


def exit_on_q(key):
    if key in ('q', 'Q', 'esc'):
        raise urwid.ExitMainLoop()


def main(args):
    app = GameApp()
    loop = urwid.MainLoop(
        urwid.Filler(app.main_layout, valign='top'),
        PALETTE,
        unhandled_input=exit_on_q,
    )
    loop.run()


if '__main__' == __name__:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)

    args = parser.parse_args()
    main(args)
