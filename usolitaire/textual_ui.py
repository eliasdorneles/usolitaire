import time
from enum import Enum
from enum import auto

from textual import events
from textual.app import ComposeResult
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Static

from usolitaire import card_render
from usolitaire.game import Card

_DOUBLE_CLICK_THRESHOLD_SECONDS = 0.4


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

    def __init__(self, sender_id: str, card: Card | None, click_type: ClickType):
        self.sender_id = sender_id
        self.card = card
        self.click_type = click_type
        super().__init__()


class TableauCardClicked(Message):
    """
    Message to signal that a card in the tableau was clicked
    """

    def __init__(
        self,
        sender_id: str | None,
        card: Card | None,
        click_type: ClickType,
        pile_index: int,
        card_index: int,
    ):
        self.sender_id = sender_id
        self.card = card
        self.click_type = click_type
        self.pile_index = pile_index
        self.card_index = card_index
        super().__init__()


class EmptyTableauClicked(Message):
    def __init__(self, sender_id: str | None, pile_index: int):
        self.sender_id = sender_id
        self.pile_index = pile_index
        super().__init__()


class MoveDirection(Enum):
    LEFT = auto()
    RIGHT = auto()
    UP = auto()
    DOWN = auto()


class MoveFocus(Message):
    """
    Message to signal that the focus should be moved
    """

    def __init__(self, sender_id: str, direction: MoveDirection, card: Card | None = None):
        self.sender_id = sender_id
        self.direction = direction
        self.card = card
        super().__init__()


class PileWidget(Static):
    top_card = reactive(None)

    can_focus = True

    def __init__(self, pile: list[Card], **kwargs) -> None:
        super().__init__(**kwargs)
        self.pile = pile
        self.update(card_render.draw_empty_card())
        self.refresh_contents()
        self.last_time_clicked = None

    def refresh_contents(self):
        self.top_card = self.pile[-1] if self.pile else None

    def watch_top_card(self, card: Card | None) -> None:
        if card:
            self.update(card_render.draw_card(card, add_rich_markup=True))
        else:
            self.update(card_render.draw_empty_card())

    def _post_click_message(self, click_type: ClickType) -> None:
        self.post_message(CardClicked(self.id, self.top_card, click_type))

    def on_click(self):
        now = time.monotonic()
        click_type = ClickType.from_click_times(now, self.last_time_clicked)
        self.last_time_clicked = now
        self._post_click_message(click_type)

    def on_key(self, event: events.Key) -> None:
        if event.key == "space":
            self.on_click()
        if event.key == "enter":
            self._post_click_message(ClickType.DOUBLE)
        elif event.key == "left" or event.key == "h":
            self.post_message(MoveFocus(self.id, MoveDirection.LEFT))
        elif event.key == "right" or event.key == "l":
            self.post_message(MoveFocus(self.id, MoveDirection.RIGHT))
        elif event.key == "up" or event.key == "k":
            self.post_message(MoveFocus(self.id, MoveDirection.UP))
        elif event.key == "down" or event.key == "j":
            self.post_message(MoveFocus(self.id, MoveDirection.DOWN))


class TableauCardWidget(Static):
    can_focus = True

    def __init__(self, card: Card, is_covered=False, **kwargs) -> None:
        super().__init__(**kwargs)
        self.card = card
        self.is_covered = is_covered
        self.last_time_clicked = None

    def compose(self) -> ComposeResult:
        yield Static(
            card_render.draw_card(self.card, only_top=self.is_covered, add_rich_markup=True)
        )

    def _post_click_message(self, click_type: ClickType) -> None:
        self.post_message(CardClicked(self.id, self.card, click_type))

    def on_click(self):
        now = time.monotonic()
        click_type = ClickType.from_click_times(now, self.last_time_clicked)
        self.last_time_clicked = now
        self._post_click_message(click_type)

    def on_key(self, event: events.Key) -> None:
        if event.key == "space":
            self.on_click()
        if event.key == "enter":
            self._post_click_message(ClickType.DOUBLE)
        elif event.key == "left" or event.key == "h":
            self.post_message(MoveFocus(self.id, MoveDirection.LEFT, self.card))
        elif event.key == "right" or event.key == "l":
            self.post_message(MoveFocus(self.id, MoveDirection.RIGHT, self.card))
        elif event.key == "up" or event.key == "k":
            self.post_message(MoveFocus(self.id, MoveDirection.UP, self.card))
        elif event.key == "down" or event.key == "j":
            self.post_message(MoveFocus(self.id, MoveDirection.DOWN, self.card))
        else:
            return
        event.stop()


class TableauPileWidget(Static):
    can_focus = True

    def __init__(self, pile: list[Card], index: int, **kwargs) -> None:
        super().__init__(**kwargs)
        self.pile = pile
        self.index = index

    def compose(self) -> ComposeResult:
        if not self.pile:
            yield Static(card_render.draw_empty_card())
            return
        for i, card in enumerate(self.pile):
            if i == len(self.pile) - 1:
                yield TableauCardWidget(card, is_covered=False)
            else:
                yield TableauCardWidget(card, is_covered=True)

    def refresh_contents(self):
        self.remove_children()
        for w in self.compose():
            self.mount(w)

    def on_card_clicked(self, event: CardClicked):
        if event.card is None:
            return
        self.post_message(
            TableauCardClicked(
                sender_id=self.id,
                card=event.card,
                click_type=event.click_type,
                pile_index=self.index,
                card_index=self.pile.index(event.card),
            )
        )

    def on_move_focus(self, event: MoveFocus):
        event.sender_id = self.id

    def on_click(self):
        if not self.pile:
            self.post_message(EmptyTableauClicked(self.id, self.index))

    def on_key(self, event: events.Key) -> None:
        if event.key in ("space", "enter"):
            if not self.pile:
                self.post_message(EmptyTableauClicked(self.id, self.index))
        elif event.key == "left" or event.key == "h":
            self.post_message(MoveFocus(self.id, MoveDirection.LEFT))
        elif event.key == "right" or event.key == "l":
            self.post_message(MoveFocus(self.id, MoveDirection.RIGHT))
        elif event.key == "up" or event.key == "k":
            self.post_message(MoveFocus(self.id, MoveDirection.UP))
        elif event.key == "down" or event.key == "j":
            self.post_message(MoveFocus(self.id, MoveDirection.DOWN))
        else:
            return
        event.stop()
