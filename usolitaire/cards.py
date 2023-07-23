def draw_empty_card(columns, rows):
    return [
        "╭"
        + "─" * (columns - 2)
        + "╮\n"
        + (rows - 2) * ("│" + " " * (columns - 2) + "│\n")
        + "╰"
        + "─" * (columns - 2)
        + "╯\n"
    ]


def draw_faced_down_card(
    columns, rows, on_pile=False, top_of_pile=False, bottom_of_pile=False
):
    face_down_middle_filling = (columns - 2) * "╬"
    if on_pile and not top_of_pile:
        filling = ["│" + face_down_middle_filling + "│\n"]
    else:
        filling = ["│" + face_down_middle_filling + "│\n"] * (rows - 2)

    if on_pile and not bottom_of_pile:
        top = "├" + "─" * (columns - 2) + "┤\n"
    else:
        top = "╭" + "─" * (columns - 2) + "╮\n"

    text = [top] + filling
    if not on_pile or top_of_pile:
        text += ["╰" + "─" * (columns - 2) + "╯\n"]

    text[-1] = text[-1].strip()

    return text
