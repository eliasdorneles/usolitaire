import time
from enum import Enum, auto

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Footer, Static

from usolitaire import card_render
from usolitaire.game import Card, Game

_DOUBLE_CLICK_THRESHOLD_SECONDS = 0.5


class ClickType(Enum):
    SINGLE = auto()
    DOUBLE = auto()

    @classmethod
    def from_click_times(cls, last_click_time, previous_click_time) -> "ClickType":
        """
        Return if it's a single or double click, based on the time between clicks
        """
        if previous_click_time is None:
            return cls.SINGLE

        if last_click_time - previous_click_time < _DOUBLE_CLICK_THRESHOLD_SECONDS:
            return cls.DOUBLE

        return cls.SINGLE


class CardClicked(Message):
    """
    Message to signal that a card was clicked
    """

    def __init__(self, widget_id: str | None, card: Card | None, click_type: ClickType):
        self.widget_id = widget_id
        self.card = card
        self.click_type = click_type
        super().__init__()


class PileWidget(Static):
    top_card = reactive(None)
    # can_focus = True  # TODO: is this needed?

    DEFAULT_CSS = """
    PileWidget {
        height: 10;
        border: transparent;
        max-width: 12;
    }
    PileWidget.focused {
        border: solid orange;
    }
    """

    def __init__(self, pile: list[Card], **kwargs) -> None:
        super().__init__(**kwargs)
        self.pile = pile
        self.update(card_render.draw_empty_card())
        self.update_top_card()
        self.last_time_clicked = None

    def update_top_card(self):
        self.top_card = self.pile[-1] if self.pile else None

    def watch_top_card(self, card: Card | None) -> None:
        if card:
            self.update(card_render.draw_card(card, add_rich_markup=True))
        else:
            self.update(card_render.draw_empty_card())

    def on_click(self):
        now = time.monotonic()
        click_type = ClickType.from_click_times(now, self.last_time_clicked)
        self.post_message(CardClicked(self.id, self.top_card, click_type))
        self.last_time_clicked = now


class TableauCardWidget(Static):
    # TODO: how to highlight the focused card?
    DEFAULT_CSS = """
    TableauCardWidget.focused {
        background: $boost;
    }
    TableauCardWidget.selected {
        background: grey;
    }
    """

    def __init__(self, card: Card, is_covered=False, **kwargs) -> None:
        super().__init__(**kwargs)
        self.card = card
        self.is_covered = is_covered

    def compose(self) -> ComposeResult:
        yield Static(
            card_render.draw_card(self.card, only_top=self.is_covered, add_rich_markup=True)
        )


class TableauPileWidget(Static):
    DEFAULT_CSS = """
    TableauPileWidget {
        max-width: 12;
        border: transparent;
    }
    TableauPileWidget.focused {
        border: solid orange;
    }
    """

    def __init__(self, pile: list[Card], **kwargs) -> None:
        super().__init__(**kwargs)
        self.pile = pile

    def compose(self) -> ComposeResult:
        for i, card in enumerate(self.pile):
            if i == len(self.pile) - 1:
                yield TableauCardWidget(card, is_covered=False)
            else:
                yield TableauCardWidget(card, is_covered=True)


class FocusRow(Enum):
    TOP = 0
    BOTTOM = 1


class FocusPosition:
    def __init__(self, row: FocusRow, pile_index: int, card_index: int | None = None):
        self.row = row
        self.pile_index = pile_index
        self.card_index = card_index

    def get_pile_id(self) -> str:
        if self.row == FocusRow.TOP:
            return "stock" if self.pile_index == 0 else "waste"
        else:
            return f"tableau{self.pile_index}"


class GameApp(App):
    BINDINGS = [
        Binding("tab", "switch_row_focus", "Switch focus", priority=True, show=True),
        Binding("left", "move_focus_left", " ", show=True),
        Binding("right", "move_focus_right", " ", show=True),
        Binding("up", "move_focus_up", " ", show=True),
        Binding("down", "move_focus_down", " Move around", show=True),
        # ("space", "select_to_move", "Select to move"),
        ("q", "quit", "Quit"),
        ("d", "toggle_dark", "Toggle dark mode"),
    ]
    CSS = """
    Screen {
        layout: grid;
        grid-size: 7;
        grid-rows: 10 100%;
    }
    """

    def __init__(self):
        super().__init__()
        self.game = Game()
        self.current_focus: FocusPosition | None = None
        self.top_last_focus: FocusPosition | None = None
        self.bottom_last_focus: FocusPosition | None = None

    def action_quit(self):
        self.exit()

    def action_switch_row_focus(self):
        """
        Switch focus between top and bottom rows
        """
        if self.current_focus is None:
            self.current_focus = FocusPosition(FocusRow.TOP, 0)
        elif self.current_focus.row == FocusRow.TOP:
            self.top_last_focus = self.current_focus
            pile_index = self.bottom_last_focus.pile_index if self.bottom_last_focus else 0
            self.current_focus = FocusPosition(FocusRow.BOTTOM, pile_index)
        else:
            self.bottom_last_focus = self.current_focus
            pile_index = self.top_last_focus.pile_index if self.top_last_focus else 0
            self.current_focus = FocusPosition(FocusRow.TOP, pile_index)

        self._update_focus()

    def _update_focus(self):
        if self.current_focus is None:
            return
        self.query(".focused").remove_class("focused")
        focused_pile = self.get_focused_pile()
        focused_pile.add_class("focused")
        focused_pile.focus()

        if self.current_focus.row == FocusRow.BOTTOM:
            if self.game.tableau[self.current_focus.pile_index]:
                self.current_focus.card_index = len(self.game.tableau[self.current_focus.pile_index]) - 1

        if self.current_focus.card_index is not None:
            focused_pile.children[self.current_focus.card_index].add_class("focused")
            focused_pile.children[self.current_focus.card_index].focus()

    def action_move_focus_left(self):
        """
        Move focus left one pile
        """
        if self.current_focus is None:
            self.current_focus = FocusPosition(FocusRow.TOP, 0)

        if self.current_focus.row == FocusRow.TOP:
            self.current_focus.pile_index = 0 if self.current_focus.pile_index == 1 else 1
        else:
            self.current_focus.pile_index = max(0, self.current_focus.pile_index - 1)
            self.current_focus.card_index = len(self.game.tableau[self.current_focus.pile_index]) - 1
        self._update_focus()

    def action_move_focus_right(self):
        """
        Move focus right one pile
        """
        if self.current_focus is None:
            self.current_focus = FocusPosition(FocusRow.TOP, 1)

        if self.current_focus.row == FocusRow.TOP:
            self.current_focus.pile_index = 1 if self.current_focus.pile_index == 0 else 0
        else:
            self.current_focus.pile_index = min(
                len(self.game.tableau) - 1, self.current_focus.pile_index + 1
            )
            self.current_focus.card_index = len(self.game.tableau[self.current_focus.pile_index]) - 1
        self._update_focus()

    def _find_next_uncovered_card(self, pile: list[Card], start_index: int) -> int:
        for i, card in enumerate(pile[start_index:], start_index):
            if card.face_up:
                return i
        return -1

    def action_move_focus_up(self):
        """
        Move focus up one card.

        If the focus is on the top row, do nothing.
        If the focus is on the bottom row, there are two cases:
        - If there are uncovered cards above the focus, move up to the next uncovered card
        - If there are no uncovered cards above the focus, move to the top row
        """
        if self.current_focus is None:
            self.current_focus = FocusPosition(FocusRow.TOP, 0)

        if self.current_focus.row == FocusRow.TOP:
            return

        focused_tableau = self.game.tableau[self.current_focus.pile_index]
        first_uncovered = self._find_next_uncovered_card(focused_tableau, 0)

        if self.current_focus.card_index is None:
            self.current_focus.card_index = first_uncovered
        elif self.current_focus.card_index == 0 or self.current_focus.card_index <= first_uncovered:
            # TODO: keep the same column, in case of first two columns
            self.action_switch_row_focus()
            return
        else:
            self.current_focus.card_index = max(first_uncovered, self.current_focus.card_index - 1)

        self._update_focus()

    def action_move_focus_down(self):
        """
        Move focus down one card.

        If the focus is on the top row, goes to the bottom row.
        If the focus is on the bottom row, there are two cases:
        - If there are uncovered cards below the focus, move down to the next uncovered card
        - If there are no uncovered cards below the focus, do nothing
        """
        if self.current_focus is None:
            self.current_focus = FocusPosition(FocusRow.BOTTOM, 0)

        if self.current_focus.row == FocusRow.TOP:
            # TODO: keep the same column, in case of first two columns
            self.action_switch_row_focus()
            return

        focused_tableau = self.game.tableau[self.current_focus.pile_index]
        first_uncovered = self._find_next_uncovered_card(focused_tableau, 0)

        if self.current_focus.card_index is None:
            self.current_focus.card_index = first_uncovered
        elif self.current_focus.card_index == len(focused_tableau) - 1:
            return
        elif first_uncovered == -1:
            return
        else:
            self.current_focus.card_index = min(
                len(focused_tableau) - 1, self.current_focus.card_index + 1
            )
        self._update_focus()

    def get_focused_pile(self) -> Widget:
        if self.current_focus is None:
            raise ValueError("No focus")
        return self.query_one("#" + self.current_focus.get_pile_id())

    def key_space(self):
        """
        Clicks the focused element.

        If on a tableau pile or on the waste, this will select the top card to move.
        If on the stock, this will deal a card to the waste.
        """
        if not self.current_focus:
            return
        if self.current_focus.row == FocusRow.TOP:
            if self.current_focus.pile_index == 0:
                self.action_deal_from_stock()
            else:
                # TODO: select top card of waste
                pass
        else:
            # TODO: select top card of tableau pile
            pass

    def compose(self) -> ComposeResult:
        yield PileWidget(self.game.stock, id="stock")
        yield PileWidget(self.game.waste, id="waste")
        yield Static("")

        for i, foundation_pile in enumerate(self.game.foundations):
            yield PileWidget(foundation_pile, id=f"foundation{i}")

        for i, tableau_pile in enumerate(self.game.tableau):
            yield TableauPileWidget(tableau_pile, id=f"tableau{i}")

        yield Footer()

    def action_deal_from_stock(self):
        if self.game.stock:
            self.game.deal_from_stock()
        else:
            self.game.restore_stock()
        self.query_one("#stock").update_top_card()
        self.query_one("#waste").update_top_card()

    # TODO: add a keypress handler that moves between the tableau piles
    # TODO: add a keypress handler that deals from the stock
    # TODO: add a keypress handler that select to move from waste or tableau
    # or send them to foundation
    def on_card_clicked(self, event: CardClicked):
        if event.widget_id == "stock":
            self.action_deal_from_stock()
        if event.widget_id == "waste":
            # TODO: if it's "double click", try to send to foundation,
            #       if it's "single click", just select the card to move
            pass
        # TODO: implement move from tableau to tableau
        # TODO: implement moving from waste to tableau
        # TODO: implement movent from waste or tableau to foundation


if __name__ == "__main__":
    app = GameApp()
    app.run()
