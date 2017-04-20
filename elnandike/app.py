#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
import urwid
from .game import Game
from .ui import CardWidget, CardPileWidget, SpacerWidget, EmptyCardWidget, PALETTE


def exit_on_q(key):
    if key in ('q', 'Q', 'esc'):
        raise urwid.ExitMainLoop()


class GameApp(object):
    def __init__(self):
        self.game = Game()
        statusbar = urwid.Text(u'Ready')

        def update_status(text):
            statusbar.set_text(text)

        def onclick(card_widget):
            # XXX: code below is meant just for testing the UI,
            # it's not related to actual game logic
            card_widget.face_up = not card_widget.face_up
            card_widget.highlighted = not card_widget.highlighted

            update_status(
                'Clicked: {}\nCard: {}\nHighlighted: {}'.format(
                    card_widget,
                    card_widget.card,
                    card_widget.highlighted,
                )
            )
            card_widget.redraw()

        def pile_card_clicked(card_widget, pile=None):
            if not pile.top.face_up:
                pile.top.face_up = True
            else:
                pile.cards.pop()
                pile.redraw()

        self.main_layout = urwid.Pile([
            urwid.Columns([
                CardWidget(self.game.stock[-1]),
                EmptyCardWidget(),
                SpacerWidget(),
                EmptyCardWidget(),
                EmptyCardWidget(),
                EmptyCardWidget(),
                EmptyCardWidget(),
            ]),
            urwid.Divider(),
            urwid.Columns([
                CardPileWidget(pile, onclick=pile_card_clicked)
                for pile in self.game.tableau
            ]),
            urwid.Divider(),
            statusbar,
        ])



def main(args):
    app = GameApp()
    if args.shell:
        from IPython import embed
        embed()
    else:
        loop = urwid.MainLoop(
            urwid.Filler(app.main_layout, valign='top'),
            PALETTE,
            unhandled_input=exit_on_q,
        )
        loop.run()


if '__main__' == __name__:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--shell', action='store_true')

    args = parser.parse_args()
    main(args)
