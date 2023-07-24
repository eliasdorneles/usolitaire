from textual.app import App, ComposeResult

from textual.widgets import Static
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
        yield Static(card_render.draw_card(self.card, only_top=self.is_covered))


class PileWidget(Static):
    DEFAULT_CSS = """
    PileWidget {
        border: solid green;
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
    def compose(self) -> ComposeResult:
        g = Game()
        with Horizontal():
            for pile in g.tableau:
                yield PileWidget(pile)

if __name__ == "__main__":
    app = GameApp()
    app.run()
