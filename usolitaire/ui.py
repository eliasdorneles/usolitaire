#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urwid
from functools import partial


PALETTE = [
    ('red', 'dark red', ''),
    ('selectedred', 'dark red', 'yellow'),
    ('selected', '', 'yellow'),
]


class SpacerWidget(urwid.WidgetWrap):
    def __init__(self, **kw):
        self.text = urwid.Text([u'        \n'] * 6, wrap='clip')
        super(SpacerWidget, self).__init__(self.text)


class EmptyCardWidget(urwid.WidgetWrap):
    def __init__(self, onclick=None, **kw):
        self.onclick = onclick
        self.text = urwid.Text(
            [
                u'╭──────╮\n',
                u'│      │\n',
                u'│      │\n',
                u'│      │\n',
                u'│      │\n',
                u'╰──────╯\n',
            ], wrap='clip')
        super(EmptyCardWidget, self).__init__(self.text)

    def selectable(self):
        return bool(self.onclick)

    def mouse_event(self, size, event, button, col, row, focus):
        if event == 'mouse press':
            if self.onclick:
                self.onclick(self)

    def redraw(self):
        """no-op"""

    def iter_widgets(self):
        return iter([])


class CardWidget(urwid.WidgetWrap):
    highlighted = False

    def __init__(self, card, playable=False, on_pile=False,
                 bottom_of_pile=False, top_of_pile=False, onclick=None):
        self._card = card
        self.playable = playable
        self.on_pile = on_pile
        self.bottom_of_pile = bottom_of_pile
        self.top_of_pile = top_of_pile
        self.text = urwid.Text(self._draw_card_text(), wrap='clip')
        self.highlighted = False
        self.onclick = onclick
        super(CardWidget, self).__init__(self.text)

    def __repr__(self):
        return '{}(card={!r}, playable={!r}, highlighted={!r}, ...)'.format(
            self.__class__.__name__, self.card, self.playable, self.highlighted,
        )

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
    def card(self):
        return self._card

    @card.setter
    def card(self, card):
        self._card = card
        self.redraw()

    @property
    def face_up(self):
        return self.card.face_up

    @face_up.setter
    def face_up(self, val):
        self.card.face_up = bool(val)
        self.redraw()

    def redraw(self):
        self.text.set_text(self._draw_card_text())


class CardPileWidget(urwid.WidgetWrap):
    def __init__(self, cards, onclick=None, index=0):
        self.cards = cards
        self.onclick = onclick
        self.pile = urwid.Pile([])
        self._update_pile()
        self.index = index
        super(CardPileWidget, self).__init__(self.pile)

    def _update_pile(self):
        if self.cards:
            bottom_cards, card_on_top = self.cards[:-1], self.cards[-1]
            card_widgets = [
                CardWidget(c,
                           onclick=partial(self.onclick, pile=self),
                           playable=c.face_up,
                           on_pile=True,
                           bottom_of_pile=(i == 0))
                for i, c in enumerate(bottom_cards)]
            card_widgets.append(
                CardWidget(card_on_top,
                           playable=True,
                           onclick=partial(self.onclick, pile=self),
                           on_pile=len(self.cards) > 1,
                           top_of_pile=True))
        else:
            card_widgets = [EmptyCardWidget(onclick=partial(self.onclick, pile=self))]
        self.pile.contents.clear()
        self.pile.contents.extend([(w, self.pile.options()) for w in card_widgets])

    def iter_widgets(self):
        for w, _ in self.pile.contents:
            yield w

    def redraw(self):
        self._update_pile()

    def selectable(self):
        return True

    def keypress(self, size, key):
        return super(CardPileWidget, self).keypress(size, key)

    def mouse_event(self, *args):
        return super(CardPileWidget, self).mouse_event(*args)

    @property
    def top(self):
        card_widget, _ = self.pile.contents[-1]
        return card_widget
