#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urwid


class Card(urwid.Widget):
    _sizing = frozenset(['fixed'])

    def render(self, size, focus=False):
        top = '╭──────╮'
        bottom = '╰──────╯'
        turned_pattern = '│╬╬╬╬╬╬│'
        return urwid.TextCanvas([top] + [turned_pattern] * 4 + [bottom], maxcol=8)

    def pack(self, size, focus=False):
        return (8, 6)
