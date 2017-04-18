#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urwid


PALETTE = [
    ('red', 'dark red', ''),
]


class CardWidget(urwid.WidgetWrap):
    def __init__(self, card, face_up=True, playable=False, on_pile=False,
                 bottom_of_pile=False, top_of_pile=False):
        self.card = card
        self._face_up = face_up
        self.playable = playable
        self.on_pile = on_pile
        self.bottom_of_pile = bottom_of_pile
        self.top_of_pile = top_of_pile
        self.text = urwid.Text(self._draw_card_text(), wrap='clip')
        super(CardWidget, self).__init__(self.text)

    def selectable(self):
        return True

    def keypress(self, size, key):
        return key

    def mouse_event(self, size, event, button, col, row, focus):
        if self.playable and event == 'mouse press':
            self.face_up = not self.face_up

    def _draw_card_text(self):
        color = 'red' if self.card.suit in ('hearts', 'diamonds') else ''
        if not self.face_up:
            if self.on_pile and not self.top_of_pile:
                filling = [u'│╬╬╬╬╬╬│\n']
            else:
                filling = [u'│╬╬╬╬╬╬│\n'] * 4
        else:
            rank, suit = (self.card.rank, self.card.suit_symbol)
            filling = [u'│', (color, '{}   {}'.format(rank.ljust(2), suit)), '│\n']
            if not self.on_pile or self.top_of_pile:
                filling += (
                    [u'│      │\n'] * 2 +
                    [u'│', (color, '{}   {}'.format(suit, rank.rjust(2))), '│\n']
                )
        top = u'├──────┤\n' if self.on_pile and not self.bottom_of_pile else u'╭──────╮\n'
        text = [top] + filling
        if not self.on_pile or self.top_of_pile:
            text += [u'╰──────╯\n']
        text[-1] = text[-1].strip()
        return text

    @property
    def face_up(self):
        return self._face_up

    @face_up.setter
    def face_up(self, val):
        self._face_up = bool(val)
        self.text.set_text(self._draw_card_text())


class CardPileWidget(urwid.WidgetWrap):
    def __init__(self, cards):
        bottom_cards, card_on_top = cards[:-1], cards[-1]
        self._card_widgets = [
            CardWidget(c, face_up=False, playable=True, on_pile=True, bottom_of_pile=(i == 0))
            for i, c in enumerate(bottom_cards)]
        self._card_widgets.append(CardWidget(card_on_top, on_pile=len(cards) > 1,
                                             top_of_pile=True, playable=True))
        self.pile = urwid.Pile(self._card_widgets)
        super(CardPileWidget, self).__init__(self.pile)

    def selectable(self):
        return True

    def keypress(self, size, key):
        return super(CardPileWidget, self).keypress(size, key)

    def mouse_event(self, *args):
        return super(CardPileWidget, self).mouse_event(*args)
