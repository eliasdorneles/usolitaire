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

app = None
shifted_number_keys = ('!', '@', '#', '$', '%', '^', '&')


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
                CardPileWidget(pile, onclick=self.pile_card_clicked, on_double_click=self.pile_card_double_clicked, index=i),
                self._tableau_columns.options())

    def _update_stock_and_waste(self):
        if self.game.stock:
            stock_widget = CardWidget(self.game.stock[-1],
                                      onclick=self.stock_clicked,
                                      playable=True)
        else:
            stock_widget = EmptyCardWidget(onclick=self.redeal_stock)
        self._top_columns.contents[0] = (stock_widget, self._top_columns.options())

        if self.game.waste:
            waste_widget = CardWidget(self.game.waste[-1],
                                      onclick=self._card_from_waste_clicked,
                                      on_double_click=self.waste_card_double_clicked,
                                      playable=True)
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
        """Iterate through all card widgets in the game"""
        for pile, _ in self._tableau_columns.contents:
            for w in pile.iter_widgets():
                yield w

        for w, _ in self._top_columns.contents:
            if isinstance(w, CardWidget):
                yield w
            else:
                iter_widgets = getattr(w, 'iter_widgets', lambda: [])
                for w in iter_widgets():
                    yield w

    def clear_selection(self):
        self.current_selection = Selection(None, None)
        for card in self.iter_allcards():
            card.highlighted = False
            card.redraw()

    def select_card(self, card_widget, pile=None):
        """Select card, or deselect if it was previously selected"""
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

    def _card_from_waste_clicked(self, card_widget):
        self.select_card(card_widget, None)

    def _card_from_tableau_clicked(self, card_widget, pile):
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

    def pile_card_clicked(self, card_widget, pile=None):
        if pile and hasattr(pile.top, 'face_up') and not pile.top.face_up:
            pile.top.face_up = True
            self.clear_selection()
            self.update_status('Neat!')
            return

        self._card_from_tableau_clicked(card_widget, pile)

    def waste_card_double_clicked(self, card_widget, pile=None):
        try:
            self.game.move_to_foundation_from_waste()
        except InvalidMove:
            self.update_status("Can't move card to foundation")
        else:
            self._update_stock_and_waste()
            self._update_foundations()


    def pile_card_double_clicked(self, card_widget, pile=None):
        if pile and hasattr(pile.top, 'face_up') and not pile.top.face_up:
            pile.top.face_up = True
            self.clear_selection()
            self.update_status('Neat!')
            return

        try:
            self.game.move_to_foundation_from_tableau(pile.index)
        except InvalidMove:
            self.update_status("Can't move card to foundation")
        else:
            pile.redraw()
            self._update_foundations()
            self.clear_selection()
            self.update_status('Great job!!')


    def update_status(self, text='', append=False):
        if append:
            text = self._statusbar.get_text()[0] + '\n' + text
        self._statusbar.set_text(text)


def unhandled_input(key):
    # Single Click the pile: 1, 2, 3, 4, 5, 6, 7
    if key in [str(x) for x in range(1, 8)]:
        selected_pile = app._tableau_columns[int(key)-1]
        selected_pile.top.onclick(selected_pile.top)

    # Double Click the pile: Shift + 1, 2, 3, 4, 5, 6, 7

    if key in shifted_number_keys:
        double_clicked_card = app._tableau_columns[shifted_number_keys.index(key)].top

        if double_clicked_card.on_double_click:
            double_clicked_card.on_double_click(double_clicked_card)

    # Stock Pile: Space or Enter

    if key in (' ', 'enter'):
        stock_pile = app._top_columns[0]
        stock_pile.onclick(stock_pile)

    # Waste Pile: 0, Shift + 0, . (for numpad)

    if key == '0':
        waste_pile = app._top_columns[1]
        waste_pile.onclick(waste_pile)

    if key in (')', '.'):
        waste_pile = app._top_columns[1]

        if waste_pile.on_double_click:
            waste_pile.on_double_click(double_clicked_card)

    # Select through the cards in each pile: q, w, e, r, t, y, u
    # (the keys below their respective numbers)

    if key in tuple('qwertyu'):
        selected_pile = app._tableau_columns['qwertyu'.index(key)]
        if isinstance(selected_pile, EmptyCardWidget):
            return

        cards = (x for x, _ in selected_pile.pile.contents)
        already_selected = any(x.highlighted for x in cards)

        for card in cards:
            if card.highlighted:
                card.onclick(card)
                already_selected = False
                continue

            if card.face_up and not already_selected:
                card.onclick(card)
                break

    # Restart Game
    if key == 'esc':
        main()

    # Exit Game

    if key in ('Q', 'x'):
        raise urwid.ExitMainLoop()


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()

    global app
    app = GameApp()
    loop = urwid.MainLoop(
        urwid.Filler(app.main_layout, valign='top'),
        PALETTE,
        unhandled_input=unhandled_input,
    )
    loop.run()


if '__main__' == __name__:
    main()
