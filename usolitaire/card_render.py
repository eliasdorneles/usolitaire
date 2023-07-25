from usolitaire.game import Card

ROWS, COLUMNS = 8, 10


def draw_empty_card():
    rows, columns = ROWS, COLUMNS
    """
    Draws an empty card.

    Used for drawing empty piles (e.g. the foundation piles).
    """
    filling = (rows - 2) * (" " * (columns - 2) + "\n")
    return add_card_borders(filling)


def draw_faced_down_card_content(only_top=False):
    rows, columns = ROWS, COLUMNS

    filling_line = (columns - 2) * "╬" + "\n"

    if only_top:
        return filling_line

    return filling_line * (rows - 2)


def draw_faced_up_card_content(card, only_top=False):
    rows, columns = ROWS, COLUMNS

    spaces = (columns - 6) * " "
    content = "{}{}{} \n".format(card.rank.ljust(2), spaces, card.suit_symbol)

    if only_top:
        return content

    content += (" " * (columns - 2) + "\n") * (rows - 4)
    content += "{}{} {}\n".format(card.suit_symbol, spaces, card.rank.rjust(2))

    return content


def _wrap_lines_with(text, wrap, wrap_right=None):
    wrap_right = wrap_right if wrap_right is not None else wrap
    return "\n".join(f"{wrap}{l}{wrap_right}" for l in text.splitlines())


def add_card_borders(text, only_top=False):
    columns = COLUMNS

    top = "╭" + "─" * (columns - 2) + "╮\n"
    bottom = "╰" + "─" * (columns - 2) + "╯"

    text = _wrap_lines_with(text, "│")

    if only_top:
        return top + text

    return top + text + "\n" + bottom


def draw_card(
    card: Card,
    only_top=False,
    add_rich_markup=False,
):
    """
    Draws a faced down card.

    If only_top is True, only the top of the card is drawn, simulating a
    card covered by other cards.
    """
    if card.face_up:
        text = draw_faced_up_card_content(card, only_top=only_top)
        if add_rich_markup:
            color = "red" if card.color == "red" else ""
            text = _wrap_lines_with(text, f"[bold {color}]", f"[/bold {color}]")
    else:
        text = draw_faced_down_card_content(only_top=only_top)

    text = add_card_borders(text, only_top=only_top)

    return text
