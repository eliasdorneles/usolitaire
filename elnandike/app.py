#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Console-based Solitaire
"""

from __future__ import print_function, absolute_import, division
import urwid
from .game import Game, InvalidMove
from .ui import CardWidget, CardPileWidget, SpacerWidget, EmptyCardWidget, PALETTE


class GameApp(object):
    def __init__(self):
        self.game = Game()
        self._statusbar = urwid.Text(u'Ready')
        self._tableau_columns = urwid.Columns([
            CardPileWidget(pile, onclick=self.pile_card_clicked, index=i)
            for i, pile in enumerate(self.game.tableau)
        ])
        self._top_columns = urwid.Columns([
            EmptyCardWidget(),
            EmptyCardWidget(),
            SpacerWidget(),
            EmptyCardWidget(),
            EmptyCardWidget(),
            EmptyCardWidget(),
            EmptyCardWidget(),
        ])
        self._update_foundations()

        self.main_layout = urwid.Pile([
            self._top_columns,
            urwid.Divider(),
            self._tableau_columns,
            urwid.Divider(),
            self._statusbar,
        ])
        self._update_stock_and_waste()

    def _update_stock_and_waste(self):
        if self.game.stock:
            stock_widget = CardWidget(self.game.stock[-1], onclick=self.stock_clicked, playable=True)
        else:
            stock_widget = EmptyCardWidget(onclick=self.redeal_stock)
        self._top_columns.contents[0] = (stock_widget, self._top_columns.options())

        if self.game.waste:
            waste_widget = CardWidget(self.game.waste[-1], onclick=self.waste_clicked, playable=True)
        else:
            waste_widget = EmptyCardWidget()
        self._top_columns.contents[1] = (waste_widget, self._top_columns.options())

    def _update_foundations(self):
        for index, pile in enumerate(self.game.foundations, 3):
            widget = CardWidget(pile[-1]) if pile else EmptyCardWidget()
            self._top_columns.contents[index] = (widget, self._top_columns.options())

    def stock_clicked(self, stock_widget):
        self.game.deal_from_stock()
        self._update_stock_and_waste()
        self.update_status('Dealt from stock')

    def redeal_stock(self, stock_widget):
        self.game.restore_stock()
        self._update_stock_and_waste()
        self.update_status('Restored stock')

    def waste_clicked(self, waste_widget):
        try:
            self.game.move_to_foundation_from_waste()
        except InvalidMove:
            self.update_status('Invalid move')
        else:
            self._update_foundations()
            self._update_stock_and_waste()
            self.update_status('Well done!')

    def pile_card_clicked(self, card_widget, pile=None):
        if not pile.top.face_up:
            pile.top.face_up = True
            self.update_status('Neat!')
        else:
            try:
                self.game.move_to_foundation_from_tableau(pile.index)
            except InvalidMove:
                self.update_status('Not implemented yet')
            else:
                pile.redraw()
                self._update_foundations()
                self.update_status('Great job!!')

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
