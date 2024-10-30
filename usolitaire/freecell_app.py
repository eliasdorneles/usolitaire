import os
from dataclasses import dataclass
from enum import Enum

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Grid
from textual.css.query import NoMatches
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, Footer, Header, Label, Static

from usolitaire.game import FreecellGame, Card
from usolitaire.textual_ui import (
    CardClicked,
    ClickType,
    EmptyTableauClicked,
    MoveDirection,
    MoveFocus,
    PileWidget,
    TableauCardClicked,
    TableauPileWidget,
)

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
            return f"freecell{self.pile_index}" if self.pile_index < 4 else f"foundation{self.pile_index - 4}"
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


 /\     /\\
{  ---'  }
{  O   O  }
~~>  V  <~~
 \  \|/  /
  -----'____
 /     \    \_
{       }\  )_\_   _
|  \_/  |/ /  \_\_/ )
 \__/  /(_/     \__/
   (__/


Thanks for playing!

[USolitaire](https://github.com/eliasdorneles/usolitaire) is a Freecell
Solitaire game made with ❤️  by [Elias Dorneles](https://github.com/eliasdorneles).

It's written in Python 🐍 and uses the [Textual](https://textual.textualize.io) framework.
"""

class EndOfGameScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(Label(END_OF_GAME_MESSAGE))
        yield Footer()

class ConfirmNewGameScreen(ModalScreen):
    BINDINGS = [("escape", "app.pop_screen", "Pop screen")]

    def compose(self) -> ComposeResult:
        yield Grid(
            Label("❔    Do you want to start a new game?"),
            Button("Yes, start new game", variant="primary", id="confirm_new_game_btn"),
            Button("No, go back", variant="default", id="cancel"),
            id="dialog",
        )

    def on_key(self, event):
        if event.key in ("left", "down"):
            self.focus_next()
        elif event.key in ("right", "up"):
            self.focus_previous()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "confirm_new_game_btn")

class MyFooter(Static):
    def __init__(self):
        super().__init__(
            "Move with the arrow keys, [bold]SPACE[/bold] clicks and [bold]ENTER[/bold] double-clicks. Or just use the mouse."
        )

class FreecellApp(App):
    BINDINGS = [
        Binding("tab", "switch_row_focus", "Switch focus", priority=True, show=True),
        Binding("shift-tab", "switch_row_focus", "Switch focus", priority=True, show=False),
        Binding("n", "request_new_game", "New game", show=True),
        Binding("d", "toggle_dark", "Toggle 🌙 mode", show=True),
        ("q", "quit", "Quit"),
    ]
    CSS_PATH = os.path.join(os.path.dirname(__file__), "freecell_app.css")

    def __init__(self):
        super().__init__()
        self.game = FreecellGame()

        self.last_focus = {
            FocusRow.TOP: FocusPosition(FocusRow.TOP, 0),
            FocusRow.BOTTOM: FocusPosition(FocusRow.BOTTOM, 0),
        }
        self._current_focus = FocusPosition(FocusRow.TOP, 0)
        self.selected_card: SelectedCardPosition | None = None
        self.playing: bool = True

    @property
    def current_focus(self) -> FocusPosition:
        return self._current_focus

    @current_focus.setter
    def current_focus(self, value: FocusPosition):
        self._current_focus = value
        self.last_focus[value.row] = value

    def action_request_new_game(self):
        self.playing = False

        def confirm_new_game(confirm):
            if confirm:
                self.game = FreecellGame()
                try:
                    self.query_one("EndOfGameScreen")
                    self.pop_screen()
                except NoMatches:
                    pass

                self._current_focus = FocusPosition(FocusRow.TOP, 0)
                self.selected_card = None
                self.refresh_contents()
                self.playing = True

        self.push_screen(ConfirmNewGameScreen(), callback=confirm_new_game)

    def compose(self) -> ComposeResult:
        yield Header()

        with Container(id="game-container"):
            for i in range(4):
                yield PileWidget(self.game.freecells[i], id=f"freecell{i}")
            
            for i in range(4):
                yield PileWidget(self.game.foundations[i], id=f"foundation{i}")

            for i in range(8):
                yield TableauPileWidget(self.game.tableau[i], i, id=f"tableau{i}")

        yield MyFooter()
        yield Footer()

    def refresh_contents(self):
        for i in range(4):
            freecell_widget = self._get_freecell_pile(i)
            freecell_widget.pile = self.game.freecells[i]
            freecell_widget.refresh_contents()

        for i in range(4):
            foundation_widget = self._get_foundation_pile(i)
            foundation_widget.pile = self.game.foundations[i]
            foundation_widget.refresh_contents()

        for i in range(8):
            tableau_widget = self._get_tableau_pile(i)
            tableau_widget.pile = self.game.tableau[i]
            tableau_widget.index = i
            tableau_widget.refresh_contents()

        self._update_focus()
        self.refresh()

    def action_quit(self):
        self.exit()

    def action_switch_row_focus(self):
        try:
            self.query_one("ConfirmNewGameScreen #dialog")
            self.screen.focus_next()
            return
        except NoMatches:
            pass

        if self.current_focus.row == FocusRow.TOP:
            self.current_focus = self.last_focus[FocusRow.BOTTOM]
        else:
            self.current_focus = self.last_focus[FocusRow.TOP]
        self._update_focus()

    def on_move_focus(self, event: MoveFocus):
        if not event.sender_id:
            return

        row, index = self._get_row_and_index(event.sender_id)
        
        if row == FocusRow.TOP:
            if event.direction == MoveDirection.RIGHT:
                self.current_focus = FocusPosition(FocusRow.TOP, min(7, index + 1))
            elif event.direction == MoveDirection.LEFT:
                self.current_focus = FocusPosition(FocusRow.TOP, max(0, index - 1))
            elif event.direction == MoveDirection.DOWN:
                self.current_focus = FocusPosition(FocusRow.BOTTOM, index % 8)
        else:  # FocusRow.BOTTOM
            if event.direction == MoveDirection.RIGHT:
                self.current_focus = FocusPosition(FocusRow.BOTTOM, min(7, index + 1))
            elif event.direction == MoveDirection.LEFT:
                self.current_focus = FocusPosition(FocusRow.BOTTOM, max(0, index - 1))
            elif event.direction == MoveDirection.UP:
                self.current_focus = FocusPosition(FocusRow.TOP, index)

        self._update_focus()

    def _get_row_and_index(self, sender_id: str) -> tuple[FocusRow, int]:
        if sender_id.startswith("freecell"):
            return FocusRow.TOP, int(sender_id[8:])
        elif sender_id.startswith("foundation"):
            return FocusRow.TOP, int(sender_id[10:]) + 4
        elif sender_id.startswith("tableau"):
            return FocusRow.BOTTOM, int(sender_id[7:])
        else:
            raise ValueError(f"Unknown sender_id: {sender_id}")

    def _update_focus(self):
        if self.current_focus is None:
            return
        focused_pile = self.query_one("#" + self.current_focus.get_pile_id())
        focused_pile.focus()

        if self.current_focus.row == FocusRow.BOTTOM and self.game.tableau[self.current_focus.pile_index]:
            if self.current_focus.card_index is None or self.current_focus.card_index >= len(
                self.game.tableau[self.current_focus.pile_index]
            ):
                self.current_focus.card_index = len(self.game.tableau[self.current_focus.pile_index]) - 1

        if self.current_focus.card_index is not None:
            focused_pile.children[self.current_focus.card_index].focus()

    def refresh_foundations(self):
        for i in range(4):
            self._get_foundation_pile(i).refresh_contents()

    def highlight_selected_cards(self):
        self.query(".selected").remove_class("selected")
        if self.selected_card is None:
            return
        pile_widget = self.query_one("#" + self.selected_card.pile_id)
        for child in pile_widget.children[self.selected_card.card_index:]:
            child.add_class("selected")

    def on_card_clicked(self, event: CardClicked):
        if event.sender_id.startswith("freecell"):
            freecell_index = int(event.sender_id[8:])
            if self.game.freecells[freecell_index] is None:
                if self.selected_card:
                    self._try_moving_selected_card_to_freecell(freecell_index)
            else:
                new_selected_card = SelectedCardPosition(
                    self.game.freecells[freecell_index], event.sender_id, 0
                )
                if new_selected_card == self.selected_card:
                    self.selected_card = None
                else:
                    self.selected_card = new_selected_card
                self.highlight_selected_cards()
        elif event.sender_id.startswith("foundation"):
            foundation_index = int(event.sender_id[10:])
            if self.selected_card:
                self._try_moving_selected_card_to_foundation(foundation_index)

    def _get_freecell_pile(self, index: int) -> PileWidget:
        return self.query_one(f"#freecell{index}", PileWidget)

    def _get_foundation_pile(self, index: int) -> PileWidget:
        return self.query_one(f"#foundation{index}", PileWidget)

    def _get_tableau_pile(self, index: int) -> TableauPileWidget:
        return self.query_one(f"#tableau{index}", TableauPileWidget)

    def refresh_tableau(self, tableau_index: int):
        self._get_tableau_pile(tableau_index).refresh_contents()

    def check_if_won(self):
        if self.game.won():
            self.push_screen(EndOfGameScreen())
            self.playing = False

    def on_tableau_card_clicked(self, event: TableauCardClicked):
        if event.click_type == ClickType.DOUBLE:
            if self.game.can_move_to_foundation(event.pile_index):
                self.game.move_to_foundation(event.pile_index)
                self.refresh_tableau(event.pile_index)
                self.refresh_foundations()
                self.selected_card = None
                self.highlight_selected_cards()
                self._update_focus()
                self.check_if_won()
        else:
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
        if src_pile_id.startswith("freecell"):
            src_index = int(src_pile_id[8:])
            if self.game.can_move_card_to_tableau(self.game.freecells[src_index], tableau_index):
                self.game.move_from_freecell_to_tableau(src_index, tableau_index)
                self._get_freecell_pile(src_index).refresh_contents()
        elif src_pile_id.startswith("tableau"):
            src_pile_index = int(src_pile_id[7:])
            if self.game.can_move_tableau_cards(src_pile_index, tableau_index, self.selected_card.card_index):
                self.game.move_tableau_cards(src_pile_index, tableau_index, self.selected_card.card_index)
                self.refresh_tableau(src_pile_index)
        self.refresh_tableau(tableau_index)
        self.selected_card = None
        self.highlight_selected_cards()

    def _try_moving_selected_card_to_freecell(self, freecell_index: int):
        src_pile_id = self.selected_card.pile_id
        if src_pile_id.startswith("tableau"):
            src_pile_index = int(src_pile_id[7:])
            if self.game.can_move_to_freecell(src_pile_index):
                self.game.move_to_freecell(src_pile_index, freecell_index)
                self.refresh_tableau(src_pile_index)
                self._get_freecell_pile(freecell_index).refresh_contents()
        self.selected_card = None
        self.highlight_selected_cards()

    def _try_moving_selected_card_to_foundation(self, foundation_index: int):
        src_pile_id = self.selected_card.pile_id
        if src_pile_id.startswith("tableau"):
            src_pile_index = int(src_pile_id[7:])
            if self.game.can_move_to_foundation(src_pile_index):
                self.game.move_to_foundation(src_pile_index)
                self.refresh_tableau(src_pile_index)
                self._get_foundation_pile(foundation_index).refresh_contents()
        elif src_pile_id.startswith("freecell"):
            src_index = int(src_pile_id[8:])
            if self.game.can_move_from_freecell_to_foundation(src_index):
                self.game.move_from_freecell_to_foundation(src_index)
                self._get_freecell_pile(src_index).refresh_contents()
                self._get_foundation_pile(foundation_index).refresh_contents()
        self.selected_card = None
        self.highlight_selected_cards()
        self.check_if_won()

    def on_empty_tableau_clicked(self, event: EmptyTableauClicked):
        if self.selected_card is None:
            return
        self._try_moving_selected_card_to_tableau(event.pile_index)

def main():
    app = FreecellApp()
    app.run()

if __name__ == "__main__":
    main()
