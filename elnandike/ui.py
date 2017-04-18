#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urwid


PALETTE = [
    ('red', 'dark red', ''),
    ('selectedred', 'dark red', 'dark green'),
    ('selected', '', 'dark green'),
]


class CardWidget(urwid.WidgetWrap):
    highlighted = False

    def __init__(self, card, face_up=True, playable=False, on_pile=False,
                 bottom_of_pile=False, top_of_pile=False, onclick=None):
        self.card = card
        self._face_up = face_up
        self.playable = playable
        self.on_pile = on_pile
        self.bottom_of_pile = bottom_of_pile
        self.top_of_pile = top_of_pile
        self.text = urwid.Text(self._draw_card_text(), wrap='clip')
        self.highlighted = False
        self.onclick = onclick
        super(CardWidget, self).__init__(self.text)

    def selectable(self):
        return True

    def keypress(self, size, key):
        return key

    def mouse_event(self, size, event, button, col, row, focus):
        if self.playable and event == 'mouse press':
            if self.onclick:
                self.onclick(self)

    def _draw_card_text(self):
        style = 'selected' if self.highlighted else ''
        redornot = 'red' if self.card.suit in ('hearts', 'diamonds') else ''
        if self.highlighted:
            redornot = 'selected' + redornot
        if not self.face_up:
            if self.on_pile and not self.top_of_pile:
                filling = [u'│', (style, u'╬╬╬╬╬╬'), u'│\n']
            else:
                filling = [u'│', (style, u'╬╬╬╬╬╬'), u'│\n'] * 4
        else:
            rank, suit = (self.card.rank, self.card.suit_symbol)
            filling = [u'│', (redornot, '{}   {}'.format(rank.ljust(2), suit)), '│\n']
            if not self.on_pile or self.top_of_pile:
                filling += (
                    [u'│', (style, u'      '), u'│\n'] * 2 +
                    [u'│', (redornot, '{}   {}'.format(suit, rank.rjust(2))), '│\n']
                )
        top = u'├──────┤\n' if self.on_pile and not self.bottom_of_pile else u'╭──────╮\n'
        text = [top] + filling
        if not self.on_pile or self.top_of_pile:
            text += [u'╰──────╯\n']

        if isinstance(text[-1], tuple):
            text[-1] = text[-1][0], text[-1][1].strip()
        else:
            text[-1] = text[-1].strip()

        return text

    @property
    def face_up(self):
        return self._face_up

    @face_up.setter
    def face_up(self, val):
        self._face_up = bool(val)
        self.redraw()

    def redraw(self):
        self.text.set_text(self._draw_card_text())



class CardPileWidget(urwid.WidgetWrap):
    def __init__(self, cards, onclick=None):
        self.onclick = onclick
        bottom_cards, card_on_top = cards[:-1], cards[-1]
        self._card_widgets = [
            CardWidget(c,
                       face_up=False,
                       playable=True,
                       onclick=onclick,
                       on_pile=True,
                       bottom_of_pile=(i == 0))
            for i, c in enumerate(bottom_cards)]
        self._card_widgets.append(
            CardWidget(card_on_top,
                       onclick=onclick,
                       on_pile=len(cards) > 1,
                       top_of_pile=True,
                       playable=True))
        self.pile = urwid.Pile(self._card_widgets)
        super(CardPileWidget, self).__init__(self.pile)

    def selectable(self):
        return True

    def keypress(self, size, key):
        return super(CardPileWidget, self).keypress(size, key)

    def mouse_event(self, *args):
        return super(CardPileWidget, self).mouse_event(*args)
