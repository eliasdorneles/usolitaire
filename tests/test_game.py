import unittest

from usolitaire import game


class GameTest(unittest.TestCase):
    def setUp(self):
        self.game = game.Game()

    def test_game_init(self):
        self.assertEqual(len(self.game.waste), 0)
        self.assertEqual([len(pile) for pile in self.game.foundations], [0, 0, 0, 0])
        self.assertEqual([len(pile) for pile in self.game.tableau], [1, 2, 3, 4, 5, 6, 7])
        self.assertEqual(len(self.game.stock), 24)
        self.assertTrue(all(not c.face_up for c in self.game.stock))
        for pile in self.game.tableau:
            self.assertTrue(all(not c.face_up for c in pile[:-1]))
            self.assertTrue(pile[-1].face_up)

    def test_game_from_stock(self):
        prev_waste_len = len(self.game.waste)
        prev_stock_len = len(self.game.stock)
        self.game.deal_from_stock()
        self.assertEqual(len(self.game.waste), prev_waste_len + 1)
        self.assertEqual(len(self.game.stock), prev_stock_len - 1)

    def test_move_tableau_pile(self):
        # Setup: Ensure we have a known state
        self.game.tableau[0] = [game.Card('K', 'spades', True)]
        self.game.tableau[1] = [game.Card('Q', 'hearts', True)]
        self.game.move_tableau_pile(0, 1)
        self.assertEqual(len(self.game.tableau[0]), 0)
        self.assertEqual(len(self.game.tableau[1]), 2)
        self.assertEqual(self.game.tableau[1][-1].rank, 'K')

    def test_move_to_foundation(self):
        # Setup: Ensure we have a known state
        self.game.tableau[0] = [game.Card('A', 'spades', True)]
        self.game.move_to_foundation_from_tableau(0)
        self.assertEqual(len(self.game.foundations[0]), 1)
        self.assertEqual(self.game.foundations[0][-1].rank, 'A')
        self.assertEqual(self.game.foundations[0][-1].suit, 'spades')

    def test_restore_stock(self):
        # Deal all cards from stock to waste
        while self.game.stock:
            self.game.deal_from_stock()
        initial_waste_count = len(self.game.waste)
        self.game.restore_stock()
        self.assertEqual(len(self.game.stock), initial_waste_count)
        self.assertEqual(len(self.game.waste), 0)

    def test_invalid_move_to_tableau(self):
        self.game.tableau[0] = [game.Card('K', 'spades', True)]
        self.game.tableau[1] = [game.Card('Q', 'spades', True)]  # Same color
        with self.assertRaises(game.InvalidMove):
            self.game.move_tableau_pile(0, 1)

    def test_invalid_move_to_foundation(self):
        self.game.tableau[0] = [game.Card('2', 'spades', True)]
        with self.assertRaises(game.InvalidMove):
            self.game.move_to_foundation_from_tableau(0)

    def test_game_not_won(self):
        self.assertFalse(self.game.won())

    def test_game_won(self):
        # Setup a winning game state
        self.game._reset_game_to_almost_won_state()
        self.assertFalse(self.game.won())
        # Move the last card to foundation
        self.game.move_to_foundation_from_waste()
        self.assertTrue(self.game.won())

    def test_can_move_from_waste_to_tableau(self):
        # Setup: Ensure we have a known state
        self.game.waste = [game.Card('Q', 'hearts', True)]
        self.game.tableau[0] = [game.Card('K', 'spades', True)]
        self.assertTrue(self.game.can_move_from_waste_to_tableau(0))

    def test_cannot_move_from_waste_to_tableau(self):
        # Setup: Ensure we have a known state
        self.game.waste = [game.Card('K', 'hearts', True)]
        self.game.tableau[0] = [game.Card('Q', 'spades', True)]
        self.assertFalse(self.game.can_move_from_waste_to_tableau(0))

    def test_can_move_to_foundation_from_tableau(self):
        # Setup: Ensure we have a known state
        self.game.tableau[0] = [game.Card('A', 'spades', True)]
        self.assertTrue(self.game.can_move_to_foundation_from_tableau(0))

    def test_cannot_move_to_foundation_from_tableau(self):
        self.game.tableau[0] = [game.Card('K', 'spades', True)]
