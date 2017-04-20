#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Console-based Solitaire
"""

from __future__ import print_function, absolute_import, division
from collections import namedtuple
import urwid
from .game import Game, InvalidMove
from .ui import CardWidget, CardPileWidget, SpacerWidget, EmptyCardWidget, PALETTE


Selection = namedtuple('Selection', 'card tableau_index')


class GameApp(object):
    def __init__(self):
        self.game = Game()
        self._statusbar = urwid.Text(u'Ready')
        self.current_selection = Selection(None, None)
        self._tableau_columns = urwid.Columns([EmptyCardWidget() for _ in range(7)])
        self._top_columns = urwid.Columns([
            EmptyCardWidget(),
            EmptyCardWidget(),
            SpacerWidget(),
            EmptyCardWidget(),
            EmptyCardWidget(),
            EmptyCardWidget(),
            EmptyCardWidget(),
        ])
        self._update_stock_and_waste()
        self._update_foundations()
        self._update_tableaus()

        self.main_layout = urwid.Pile([
            self._top_columns,
            urwid.Divider(),
            self._tableau_columns,
            urwid.Divider(),
            self._statusbar,
        ])

    def _update_tableaus(self):
        for i, pile in enumerate(self.game.tableau):
            self._tableau_columns.contents[i] = (
                CardPileWidget(pile, onclick=self.pile_card_clicked, index=i),
                self._tableau_columns.options())

    def _update_stock_and_waste(self):
        if self.game.stock:
            stock_widget = CardWidget(self.game.stock[-1], onclick=self.stock_clicked, playable=True)
        else:
            stock_widget = EmptyCardWidget(onclick=self.redeal_stock)
        self._top_columns.contents[0] = (stock_widget, self._top_columns.options())

        if self.game.waste:
            waste_widget = CardWidget(self.game.waste[-1], onclick=self.pile_card_clicked, playable=True)
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
        self.clear_selection()

    def redeal_stock(self, stock_widget):
        self.game.restore_stock()
        self._update_stock_and_waste()
        self.update_status('Restored stock')
        self.clear_selection()

    def iter_allcards(self):
        for pile, _ in self._tableau_columns.contents:
            for w in pile.iter_widgets():
                yield w

        for w, _ in self._top_columns.contents:
            iter_widgets = getattr(w, 'iter_widgets', lambda: [])
            for w in iter_widgets():
                yield w

    def clear_selection(self):
        self.current_selection = Selection(None, None)
        for card in self.iter_allcards():
            card.highlighted = False
            card.redraw()
        self.update_status('Cleared selection', append=True)

    def select_card(self, card_widget, pile=None):
        should_highlight = not card_widget.highlighted

        for card in self.iter_allcards():
            card.highlighted = False

        card_widget.highlighted = should_highlight

        if should_highlight:
            self.current_selection = Selection(card_widget, getattr(pile, 'index', None))
        else:
            self.current_selection = Selection(None, None)

        for card in self.iter_allcards():
            card.redraw()
        self.update_status('should_highlight: %s' % should_highlight)

    def pile_card_clicked(self, card_widget, pile=None):
        if pile and hasattr(pile.top, 'face_up') and not pile.top.face_up:
            pile.top.face_up = True
            self.clear_selection()
            self.update_status('Neat!')
            return

        if pile is None:
            # assume clicked card it's from waste
            if self.game.waste and card_widget.card == self.game.waste[-1]:
                try:
                    self.game.move_to_foundation_from_waste()
                except InvalidMove:
                    # TODO: why isn't selectin from waste highlighting?
                    self.select_card(card_widget, pile)
                else:
                    self._update_stock_and_waste()
                    self._update_foundations()
            else:
                self.update_status('Invalid move')
        else:
            # assume clicked card it's from a tableau
            try:
                self.game.move_to_foundation_from_tableau(pile.index)
            except InvalidMove:
                if not self.current_selection.card or self.current_selection.card == card_widget:
                    self.select_card(card_widget, pile)
                    return

                src_index = self.current_selection.tableau_index
                try:
                    if src_index is None:
                        self.game.move_from_waste_to_tableau(pile.index)
                    else:
                        self.game.move_tableau_pile(src_index, pile.index)
                except InvalidMove:
                    self.update_status('Invalid move: %r %r' % (src_index, pile.index))
                else:
                    self._update_stock_and_waste()
                    self._update_tableaus()
                    self.clear_selection()
            else:
                pile.redraw()
                self._update_foundations()
                self.clear_selection()
                self.update_status('Great job!!')

    def update_status(self, text='', append=False):
        if append:
            text = self._statusbar.get_text()[0] + '\n' + text
        if self.current_selection:
            text += '\nCurrent selection: %r' % (self.current_selection,)
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
