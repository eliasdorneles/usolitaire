from textual.app import App, ComposeResult

from textual.reactive import reactive
from textual.widgets import Static
from textual.widgets import Footer
from usolitaire.game import Card
from usolitaire.game import Game
from usolitaire import card_render


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

    def action_quit(self):
        self.exit()

    def compose(self) -> ComposeResult:
        g = Game()
        yield PileWidget(g.stock, id="stock")
        yield PileWidget(g.waste, id="waste")
        yield Static("")
        yield PileWidget(g.foundations[0], id="foundation0")
        yield PileWidget(g.foundations[1], id="foundation1")
        yield PileWidget(g.foundations[2], id="foundation2")
        yield PileWidget(g.foundations[3], id="foundation3")
        for pile in g.tableau:
            yield TableauPileWidget(pile)
        yield Footer()


if __name__ == "__main__":
    app = GameApp()
    app.run()
