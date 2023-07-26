from dataclasses import dataclass
from enum import Enum

from textual.app import App
from textual.app import ComposeResult
from textual.binding import Binding
from textual.widget import Widget
from textual.widgets import Footer
from textual.widgets import Static

from usolitaire.game import Card
from usolitaire.game import Game
from usolitaire.textual_ui import CardClicked
from usolitaire.textual_ui import ClickType
from usolitaire.textual_ui import MoveDirection
from usolitaire.textual_ui import MoveFocus
from usolitaire.textual_ui import PileWidget
from usolitaire.textual_ui import TableauCardClicked
from usolitaire.textual_ui import TableauPileWidget


class FocusRow(Enum):
    TOP = 0
    BOTTOM = 1


@dataclass
class FocusPosition:
    row: FocusRow
    pile_index: int
    card_index: int | None = None

    def get_pile_id(self) -> str:
        if self.row == FocusRow.TOP:
            return "stock" if self.pile_index == 0 else "waste"
        else:
            return f"tableau{self.pile_index}"


@dataclass
class SelectedCardPosition:
    card: Card
    pile_id: str
    card_index: int


class GameApp(App):
    BINDINGS = [
        Binding("tab", "switch_row_focus", "Switch focus", priority=True, show=True),
        ("ctrl+d", "deal_from_stock", "Deal from stock"),
        ("q", "quit", "Quit"),
        Binding("d", "toggle_dark", "Toggle dark mode", show=False),
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
        self.last_focus = {
            FocusRow.TOP: FocusPosition(FocusRow.TOP, 0),
            FocusRow.BOTTOM: FocusPosition(FocusRow.BOTTOM, 0),
        }
        self._current_focus = FocusPosition(FocusRow.TOP, 0)
        self.selected_card: SelectedCardPosition | None = None

    @property
    def current_focus(self) -> FocusPosition:
        return self._current_focus

    @current_focus.setter
    def current_focus(self, value: FocusPosition):
        self._current_focus = value
        self.last_focus[value.row] = value

    def compose(self) -> ComposeResult:
        yield PileWidget(self.game.stock, id="stock")
        yield PileWidget(self.game.waste, id="waste")
        yield Static("")

        for i, foundation_pile in enumerate(self.game.foundations):
            yield PileWidget(foundation_pile, id=f"foundation{i}")

        for i, tableau_pile in enumerate(self.game.tableau):
            yield TableauPileWidget(tableau_pile, i, id=f"tableau{i}")

        yield Footer()

    def action_quit(self):
        self.exit()

    def action_switch_row_focus(self):
        print("SWITCH_FOCUS")
        if self.current_focus.row == FocusRow.TOP:
            self.current_focus = self.last_focus[FocusRow.BOTTOM]
        else:
            self.current_focus = self.last_focus[FocusRow.TOP]
        self._update_focus()

    def on_move_focus(self, event: MoveFocus):
        print(f"MOVE_FOCUS: sender={event.sender_id} direction={event.direction}")
        if not event.sender_id:
            return  # leave this case to be handled by the tableau pile widget

        if event.sender_id == "stock":
            if event.direction == MoveDirection.RIGHT:
                self.current_focus = FocusPosition(FocusRow.TOP, 1)
            elif event.direction == MoveDirection.DOWN:
                self.current_focus = FocusPosition(FocusRow.BOTTOM, 0)
        elif event.sender_id == "waste":
            if event.direction == MoveDirection.LEFT:
                self.current_focus = FocusPosition(FocusRow.TOP, 0)
            elif event.direction == MoveDirection.DOWN:
                self.current_focus = FocusPosition(FocusRow.BOTTOM, 1)
        elif event.sender_id and event.sender_id.startswith("tableau"):
            tableau_index = int(event.sender_id[7:])
            if event.direction == MoveDirection.UP:
                self.current_focus = FocusPosition(FocusRow.TOP, min(1, tableau_index))
            elif event.direction == MoveDirection.LEFT:
                if tableau_index == 0:
                    return
                self.current_focus = FocusPosition(FocusRow.BOTTOM, tableau_index - 1)
            elif event.direction == MoveDirection.RIGHT:
                if tableau_index == len(self.game.tableau) - 1:
                    return
                self.current_focus = FocusPosition(FocusRow.BOTTOM, tableau_index + 1)
        self._update_focus()

    def _update_focus(self):
        if self.current_focus is None:
            return
        focused_pile = self.query_one("#" + self.current_focus.get_pile_id())
        focused_pile.focus()

        if self.current_focus.row == FocusRow.BOTTOM:
            if self.game.tableau[self.current_focus.pile_index]:
                self.current_focus.card_index = (
                    len(self.game.tableau[self.current_focus.pile_index]) - 1
                )

        if self.current_focus.card_index is not None:
            focused_pile.children[self.current_focus.card_index].focus()

    def action_deal_from_stock(self):
        if self.game.stock:
            self.game.deal_from_stock()
        else:
            self.game.restore_stock()
        self.query_one("#stock").refresh_contents()
        self.query_one("#waste").refresh_contents()

    def refresh_foundations(self):
        for i in range(4):
            self.query_one(f"#foundation{i}").refresh_contents()

    def highlight_selected_cards(self):
        self.query(".selected").remove_class("selected")
        if self.selected_card is None:
            return
        if self.selected_card.pile_id == "waste":
            pile_widget = self.query_one("#waste")
            pile_widget.add_class("selected")
        else:
            pile_widget = self.query_one("#" + self.selected_card.pile_id)
            for child in pile_widget.children[self.selected_card.card_index :]:
                child.add_class("selected")

    # TODO: add a keypress handler that moves between the tableau piles
    # TODO: add a keypress handler that select to move from waste or tableau
    # TODO: check if moves are valid before making them
    def on_card_clicked(self, event: CardClicked):
        if event.sender_id == "stock":
            self.action_deal_from_stock()
        if event.sender_id == "waste":
            if (
                event.click_type == ClickType.DOUBLE
                and self.game.can_move_to_foundation_from_waste()
            ):
                self.game.move_to_foundation_from_waste()
                self.query_one("#waste").refresh_contents()
                self.refresh_foundations()
            else:
                if not self.game.waste:
                    return
                new_selected_card = SelectedCardPosition(
                    self.game.waste[-1], "waste", len(self.game.waste) - 1
                )
                if new_selected_card == self.selected_card:
                    self.selected_card = None
                else:
                    self.selected_card = new_selected_card
                self.highlight_selected_cards()

    def refresh_tableau(self, tableau_index: int):
        self.query_one(f"#tableau{tableau_index}").refresh_contents()

    def on_tableau_card_clicked(self, event: TableauCardClicked):
        print("EVENT HERE:", event.sender_id, event.pile_index, event.card_index)
        if event.click_type == ClickType.DOUBLE:
            if self.game.can_move_to_foundation_from_tableau(event.pile_index):
                self.game.move_to_foundation_from_tableau(event.pile_index)
                self.refresh_tableau(event.pile_index)
                self.refresh_foundations()
                self.selected_card = None
                self.highlight_selected_cards()
            else:
                pass  # TODO: just select
        else:
            if not event.card.face_up:
                event.card.face_up = True
                self.refresh_tableau(event.pile_index)
            pass
            # TODO: implement move from tableau to tableau
            # TODO: implement moving from waste to tableau
            # TODO: implement movent from waste or tableau to foundation


if __name__ == "__main__":
    app = GameApp()
    app.run()
