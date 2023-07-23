import unittest
from usolitaire import game


class GameTest(unittest.TestCase):
    def setUp(self):
        self.game = game.Game()

    def test_game_init(self):
        self.assertEqual(len(self.game.waste), 0)
        self.assertEqual([len(pile) for pile in self.game.foundations], [0, 0, 0, 0])
        self.assertEqual(
            [len(pile) for pile in self.game.tableau], [1, 2, 3, 4, 5, 6, 7]
        )
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
