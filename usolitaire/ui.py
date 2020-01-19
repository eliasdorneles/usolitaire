#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urwid
from functools import partial
import time

PALETTE = [
    ('red', 'dark red', ''),
    ('selectedred', 'dark red', 'yellow'),
    ('selected', '', 'yellow'),
]

SIZE_MOD = {'medium': (8,6)}


class BaseCardWidget(urwid.WidgetWrap):
    def __init__(self, *args, card_size='medium', **kw):
        self.card_columns, self.card_rows = SIZE_MOD[card_size]
        super(BaseCardWidget, self).__init__(*args, **kw)
        self.redraw()


    def redraw(self):
        self.text.set_text(self._draw_card_text())

    def _draw_card_text(self):
        raise NotImplementedError



class SpacerWidget(BaseCardWidget):
    def __init__(self, **kw):

        self.text = urwid.Text('', wrap='clip')
        super(SpacerWidget, self).__init__(self.text)

    def _draw_card_text(self):
        return [u' '* self.card_columns +'\n'] * self.card_rows


class EmptyCardWidget(BaseCardWidget):
    def __init__(self, onclick=None, **kw):
        self.onclick = onclick
        self.on_double_click = None
        self.text = urwid.Text('', wrap='clip')

        super(EmptyCardWidget, self).__init__(self.text)

    def _draw_card_text(self):
        return [
                u'╭' + '─' * (self.card_columns-2) + '╮\n' 
                + (self.card_rows-2) * (u'│'+ ' ' * (self.card_columns-2) + '│\n')
                + u'╰' + '─' * (self.card_columns-2) + '╯\n'
            ]

    def selectable(self):
        return bool(self.onclick)

    def keypress(self, size, key):
        return key

    def mouse_event(self, size, event, button, col, row, focus):
        if event == 'mouse press':
            if self.onclick:
                self.onclick(self)

    def iter_widgets(self):
        return iter([])


class CardWidget(BaseCardWidget):
    highlighted = False

    def __init__(self, card, playable=False, on_pile=False,
                 bottom_of_pile=False, top_of_pile=False, onclick=None, on_double_click=None):
        self._card = card
        self.playable = playable
        self.on_pile = on_pile
        self.bottom_of_pile = bottom_of_pile
        self.top_of_pile = top_of_pile
        self.text = urwid.Text('', wrap='clip')
        self.highlighted = False
        self.onclick = onclick
        self.on_double_click = on_double_click
        self.last_time_clicked = None
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
            now = time.time()
            if (self.last_time_clicked and (now - self.last_time_clicked < 0.5)):
                if self.on_double_click:
                    self.on_double_click(self)
            else:
                if self.onclick:
                    self.onclick(self)
            self.last_time_clicked = now

    def _draw_card_text(self):
        columns, rows = self.card_columns, self.card_rows

        style = 'selected' if self.highlighted else ''
        redornot = 'red' if self.card.suit in ('hearts', 'diamonds') else ''
        if self.highlighted:
            redornot = 'selected' + redornot
        if not self.face_up:
            face_down_middle_filling = (columns-2) * u'╬'
            if self.on_pile and not self.top_of_pile:
                filling = [u'│', (style, face_down_middle_filling), u'│\n']
            else:
                filling = [u'│', (style, face_down_middle_filling), u'│\n'] * (rows-2)
        else:
            rank, suit = (self.card.rank, self.card.suit_symbol)
            spaces = (columns-5) * ' '
            filling = [u'│', (redornot, u'{}{}{}'.format(rank.ljust(2), spaces, suit)), u'│\n']
            if not self.on_pile or self.top_of_pile:
                filling += (
                    [u'│', (style, u' ' * (columns-2)), u'│\n'] * (rows-4) +
                    [u'│', (redornot, u'{}{}{}'.format(suit, spaces,rank.rjust(2))), u'│\n']
                )
         

        if self.on_pile and not self.bottom_of_pile: 
            top = u'├'+ '─' * (columns-2) +'┤\n'
        else: 
            top = u'╭'+ '─' * (columns-2) +'╮\n'

        text = [top] + filling
        if not self.on_pile or self.top_of_pile:
            text += [u'╰' + '─' * (columns-2) + '╯\n']

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



class CardPileWidget(urwid.WidgetWrap):
    def __init__(self, cards, onclick=None, index=0, on_double_click=None):
        self.cards = cards
        self.onclick = onclick
        self.on_double_click = on_double_click
        self.pile = urwid.Pile([])
        self._update_pile()
        self.index = index
        super(CardPileWidget, self).__init__(self.pile)

    def _update_pile(self):
        if self.cards:
            bottom_cards, card_on_top = self.cards[:-1], self.cards[-1]
            card_widgets = [
                CardWidget(c,
                           onclick=self.callback(self.onclick),
                           on_double_click=self.callback(self.on_double_click),
                           playable=c.face_up,
                           on_pile=True,
                           bottom_of_pile=(i == 0))
                for i, c in enumerate(bottom_cards)]
            card_widgets.append(
                CardWidget(card_on_top,
                           playable=True,
                           onclick=self.callback(self.onclick),
                           on_double_click=self.callback(self.on_double_click),
                           on_pile=len(self.cards) > 1,
                           top_of_pile=True))
        else:
            card_widgets = [EmptyCardWidget(onclick=self.callback(self.onclick))]
        self.pile.contents[:] = []
        self.pile.contents.extend([(w, self.pile.options()) for w in card_widgets])

    def callback(self, callback):
        return partial(callback, pile=self) if callback else None

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
