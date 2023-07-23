from textual.app import App, ComposeResult

from textual.widgets import Static


class Card(Static):
    def __init__(self, rank: str, suit: str, **kwargs):
        super().__init__(**kwargs)
        self.rank = rank
        self.suit = suit
        self.face_up = False

    def compose(self) -> ComposeResult:
        return Static("TODO")
