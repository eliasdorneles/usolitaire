#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urwid


PALETTE = [
    ('red', 'dark red', ''),
]


class CardWidget(urwid.WidgetWrap):
    def __init__(self, card, turned=False):
        self.card = card
        self._turned = turned
        self.text = urwid.Text(self._draw_card_text(), wrap='clip')
        super(CardWidget, self).__init__(self.text)

    def selectable(self):
        return True

    def keypress(self, size, key):
        return key

    def mouse_event(self, size, event, button, col, row, focus):
        if event == 'mouse press':
            self.turned = not self.turned

    def _draw_card_text(self):
        color = 'red' if self.card.suit in ('hearts', 'diamonds') else ''
        if self.turned:
            filling = [u'│╬╬╬╬╬╬│\n'] * 4
        else:
            rank, suit = (self.card.rank, self.card.suit_symbol)
            filling = (
                [u'│', (color, '{}   {}'.format(rank.ljust(2), suit)), '│\n'] +
                [u'│      │\n'] * 2 +
                [u'│', (color, '{}   {}'.format(suit, rank.rjust(2))), '│\n']
            )
        return [u'╭──────╮\n'] + filling + [u'╰──────╯\n']

    @property
    def turned(self):
        return self._turned

    @turned.setter
    def turned(self, val):
        self._turned = bool(val)
        self.text.set_text(self._draw_card_text())
