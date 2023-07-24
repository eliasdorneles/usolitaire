from textual.app import App, ComposeResult

from textual.reactive import reactive
from textual.widgets import Static
from textual.widgets import Footer
from textual.containers import Horizontal
from usolitaire.game import Card
from usolitaire.game import Game
from usolitaire import card_render


class CardWidget(Static):
    def __init__(self, card: Card, is_covered=False, **kwargs) -> None:
        super().__init__(**kwargs)
        self.card = card
        self.is_covered = is_covered

    def compose(self) -> ComposeResult:
        yield Static(
            card_render.draw_card(
                self.card,
                only_top=self.is_covered,
                add_rich_markup=True,
            )
        )


class StockPileWidget(Static):
    top_card = reactive(None)

    DEFAULT_CSS = """
    StockPileWidget {
        height: 8;
    }
    """

    def __init__(self, pile: list[Card], **kwargs) -> None:
        super().__init__(**kwargs)
        self.pile = pile
        self.update_top_card()

    def update_top_card(self):
        self.top_card = self.pile[0] if self.pile else None

    def watch_top_card(self, card: Card | None) -> None:
        if card:
            self.update(
                card_render.draw_card(
                    card,
                    add_rich_markup=True,
                )
            )
        else:
            self.update(card_render.draw_empty_card())


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
    .top_piles {
        height: 10;
    }
    """

    def action_quit(self):
        self.exit()

    def compose(self) -> ComposeResult:
        g = Game()
        with Horizontal(classes="top_piles"):
            yield StockPileWidget(g.stock)
            # TODO: add waste, spacer and the 4 foundations
        with Horizontal():
            for pile in g.tableau:
                yield TableauPileWidget(pile)
        yield Footer()


if __name__ == "__main__":
    app = GameApp()
    app.run()
