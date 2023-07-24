from textual.app import App, ComposeResult

from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Footer
from textual.widgets import Static
from usolitaire.game import Card
from usolitaire.game import Game
from usolitaire import card_render


class CardClicked(Message):
    """
    Message to signal that a card was clicked
    """

    def __init__(self, widget_id: str | None, card: Card | None):
        self.widget_id = widget_id
        self.card = card
        super().__init__()


class PileWidget(Static):
    top_card = reactive(None)

    DEFAULT_CSS = """
    PileWidget {
        height: 8;
        max-width: 12;
    }
    """

    def __init__(self, pile: list[Card], **kwargs) -> None:
        super().__init__(**kwargs)
        self.pile = pile
        self.update(card_render.draw_empty_card())
        self.update_top_card()

    def update_top_card(self):
        self.top_card = self.pile[-1] if self.pile else None

    def watch_top_card(self, card: Card | None) -> None:
        if card:
            self.update(card_render.draw_card(card, add_rich_markup=True))
        else:
            self.update(card_render.draw_empty_card())

    def on_click(self):
        self.post_message(CardClicked(self.id, self.top_card))


class CardWidget(Static):
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
    }
    """

    def __init__(self, pile: list[Card], **kwargs) -> None:
        super().__init__(**kwargs)
        self.pile = pile

    def compose(self) -> ComposeResult:
        for i, card in enumerate(self.pile):
            if i == len(self.pile) - 1:
                yield CardWidget(card, is_covered=False)
            else:
                yield CardWidget(card, is_covered=True)


class GameApp(App):
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "quit", "Quit"),
    ]
    CSS = """
    Screen {
        layout: grid;
        grid-size: 7;
        grid-rows: 8 100%;
    }
    """
    def __init__(self):
        super().__init__()
        self.game = Game()

    def action_quit(self):
        self.exit()

    def compose(self) -> ComposeResult:
        yield PileWidget(self.game.stock, id="stock")
        yield PileWidget(self.game.waste, id="waste")
        yield Static("")

        for i, foundation_pile in enumerate(self.game.foundations):
            yield PileWidget(foundation_pile, id=f"foundation{i}")

        for i, tableau_pile in enumerate(self.game.tableau):
            yield TableauPileWidget(tableau_pile, id=f"tableau{i}")

        yield Footer()

    def on_card_clicked(self, event: CardClicked):
        if event.widget_id == "stock":
            if event.card is None:
                self.game.restore_stock()
            else:
                self.game.deal_from_stock()
            self.query_one("#stock").update_top_card()
            self.query_one("#waste").update_top_card()


if __name__ == "__main__":
    app = GameApp()
    app.run()
