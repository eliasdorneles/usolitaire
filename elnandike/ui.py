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
        self.text = urwid.Text(self._draw_card_text())
        super(CardWidget, self).__init__(self.text)

    def selectable(self):
        return True

    def keypress(self, *a, **kw):
        # TODO: figure how to delegate event without calling keypress for Text()
        super(CardWidget, self).keypress(*a, **kw)

    def mouse_event(self, size, event, button, col, row, focus):
        if event == 'mouse press':
            self.turned = not self.turned

    def _draw_card_text(self):
        color = 'red' if self.card.suit in ('hearts', 'diamonds') else ''
        top = u'╭──────╮\n'
        bottom = u'╰──────╯\n'
        turned_pattern = u'│╬╬╬╬╬╬│\n'
        if self.turned:
            filling = [turned_pattern] * 4
        else:
            rank, suit = (self.card.rank, self.card.suit_symbol)
            filling = (
                [u'│', (color, '{}   {}'.format(rank.ljust(2), suit)), '│\n'] +
                [u'│      │\n'] * 2 +
                [u'│', (color, '{}   {}'.format(suit, rank.rjust(2))), '│\n']
            )
        text = [top] + filling + [bottom]
        return text

    @property
    def turned(self):
        return self._turned

    @turned.setter
    def turned(self, val):
        self._turned = bool(val)
        self.text.set_text(self._draw_card_text())
