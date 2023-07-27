===============================
usolitaire
===============================


.. image:: https://img.shields.io/pypi/v/usolitaire.svg
        :target: https://pypi.python.org/pypi/usolitaire

.. image:: https://img.shields.io/travis/eliasdorneles/usolitaire.svg
        :target: https://travis-ci.org/eliasdorneles/usolitaire


Play solitaire in your terminal.

Point and click to move cards, or use the keyboard shortcuts.

Install with:

    pip install usolitaire

Run with:

    usolitaire

To run from sources, you can run with:

    python -m usolitaire.app

.. image:: https://raw.githubusercontent.com/eliasdorneles/usolitaire/master/screenshot-usolitaire.png

* Free software: MIT license


History
-------

I built the first version of this app in 2017 using the `urwid`_ library, while
I was attending `Recurse Center`_.

In 2023, after attending Europython and learning the `Textual`_ framework,
which solved all the gripes I had with ``urwid`` before, I decided to rewrite
it in Textual and added the features that were missing.

.. _urwid: https://urwid.org
.. _Recurse Center: https://www.recurse.com/
.. _Textual: https://textual.textualize.io
