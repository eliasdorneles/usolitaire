"""
Console-based Klondike Solitaire game.
"""
import argparse
import os
from dataclasses import dataclass
from enum import Enum

from textual.app import App
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Footer
from textual.widgets import Header
from textual.widgets import Static
from textual.widgets import Markdown

from usolitaire.game import Card
from usolitaire.game import Game
from usolitaire.textual_ui import CardClicked
from usolitaire.textual_ui import ClickType
from usolitaire.textual_ui import EmptyTableauClicked
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


END_OF_GAME_MESSAGE = """
# Congratulations! You won! 🎉

### You did it! 🏆

Here is a cat for you:

```
 /\     /\\
{  `---'  }
{  O   O  }
~~>  V  <~~
 \  \|/  /
  `-----'____
  /     \    \_
 {       }\  )_\_   _
 |  \_/  |/ /  \_\_/ )
  \__/  /(_/     \__/
    (__/
```

Thanks for playing!

[USolitaire](https://github.com/eliasdorneles/usolitaire) is a Klondike
Solitaire game made with ❤️  by [Elias Dorneles](https://github.com/eliasdorneles).

It's written in Python 🐍 and uses the [Textual](https://textual.textualize.io) framework.
"""


class MyFooter(Static):
    def __init__(self):
        super().__init__(
            "Move with the arrow keys, [bold]SPACE[/bold] clicks and [bold]ENTER[/bold] double-clicks. Or just use the mouse."
        )


class USolitaire(App):
    BINDINGS = [
        Binding("tab", "switch_row_focus", "Switch focus", priority=True, show=False),
        Binding("shift-tab", "switch_row_focus", "Switch focus", priority=True, show=False),
        Binding("ctrl+d", "deal_from_stock", "Deal from stock", show=True),
        Binding("d", "toggle_dark", "Toggle 🌙 mode", show=True),
        ("q", "quit", "Quit"),
    ]
    CSS_PATH = os.path.join(os.path.dirname(__file__), "textual_app.css")

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
        yield Header()

        with Container(id="game-container"):
            yield PileWidget(self.game.stock, id="stock")
            yield PileWidget(self.game.waste, id="waste")
            yield Static(
                ""
            )  # needed to occupy the space on the grid between waste and foundations

            for i, foundation_pile in enumerate(self.game.foundations):
                yield PileWidget(foundation_pile, id=f"foundation{i}")

            for i, tableau_pile in enumerate(self.game.tableau):
                yield TableauPileWidget(tableau_pile, i, id=f"tableau{i}")

        yield MyFooter()
        yield Footer()

    def action_quit(self):
        self.exit()

    def action_switch_row_focus(self):
        print(self.query_one("Footer").get_component_styles("footer--highlight").rich_style)
        if self.current_focus.row == FocusRow.TOP:
            self.current_focus = self.last_focus[FocusRow.BOTTOM]
        else:
            self.current_focus = self.last_focus[FocusRow.TOP]
        self._update_focus()

    def on_move_focus(self, event: MoveFocus):
        print(
            f"MOVE_FOCUS: sender={event.sender_id} direction={event.direction} card={event.card}"
        )
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
                card_index = self.current_focus.card_index
                if card_index and self.game.tableau[tableau_index][card_index - 1].face_up:
                    self.current_focus.card_index -= 1
                else:
                    self.current_focus = FocusPosition(FocusRow.TOP, min(1, tableau_index))
            elif event.direction == MoveDirection.DOWN:
                if self.current_focus.card_index is None:
                    self.current_focus = FocusPosition(FocusRow.BOTTOM, tableau_index)
                elif self.current_focus.card_index < len(self.game.tableau[tableau_index]) - 1:
                    self.current_focus.card_index += 1
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

        if (
            self.current_focus.row == FocusRow.BOTTOM
            and self.game.tableau[self.current_focus.pile_index]
        ):
            if self.current_focus.card_index is None or self.current_focus.card_index >= len(
                self.game.tableau[self.current_focus.pile_index]
            ):
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
                self.check_if_won()
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

    def check_if_won(self):
        if self.game.won():
            self.query("#game-container").remove()
            self.query("#help-text").remove()
            self.mount(Container(Markdown(END_OF_GAME_MESSAGE), id="end-game"))

    def on_tableau_card_clicked(self, event: TableauCardClicked):
        if event.click_type == ClickType.DOUBLE:
            if self.game.can_move_to_foundation_from_tableau(event.pile_index):
                self.game.move_to_foundation_from_tableau(event.pile_index)
                self.refresh_tableau(event.pile_index)
                self.refresh_foundations()
                self.selected_card = None
                self.highlight_selected_cards()
                self._update_focus()
                self.check_if_won()
        else:
            if not event.card.face_up:
                event.card.face_up = True
                self.current_focus = FocusPosition(FocusRow.BOTTOM, event.pile_index)
                self.refresh_tableau(event.pile_index)
                self._update_focus()
                return

            target_card = SelectedCardPosition(
                event.card, f"tableau{event.pile_index}", event.card_index
            )
            if target_card == self.selected_card:
                self.selected_card = None
            else:
                if self.selected_card:
                    target_pile_index = int(target_card.pile_id[7:])
                    self._try_moving_selected_card_to_tableau(target_pile_index)
                    self.selected_card = None
                else:
                    self.selected_card = target_card
            self.highlight_selected_cards()

    def _try_moving_selected_card_to_tableau(self, tableau_index: int):
        src_pile_id = self.selected_card.pile_id
        if src_pile_id == "waste":
            if self.game.can_move_from_waste_to_tableau(tableau_index):
                self.game.move_from_waste_to_tableau(tableau_index)
                self.query_one("#waste").refresh_contents()
        else:
            src_pile_index = int(self.selected_card.pile_id[7:])
            if self.game.can_move_card_to_tableau(self.selected_card.card, tableau_index):
                self.game.move_tableau_pile(src_pile_index, tableau_index)
                self.refresh_tableau(src_pile_index)
        self.refresh_tableau(tableau_index)
        self.selected_card = None
        self.highlight_selected_cards()

    def on_empty_tableau_clicked(self, event: EmptyTableauClicked):
        if self.selected_card is None:
            return
        self._try_moving_selected_card_to_tableau(event.pile_index)


def main():
    # TODO: add an argument to reduce size
    parser = argparse.ArgumentParser()
    parser.parse_args()

    app = USolitaire()
    app.run()


if __name__ == "__main__":
    main()
