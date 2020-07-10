import unittest

from rlcard.games.shortlimitholdem.utils import ShortHand as ShortHand

class TestShortLimitHoldemUtils(unittest.TestCase):
    def test_has_ace_pair(self):
        s = ShortHand(['HA', 'HT', 'H7', 'S8', 'S9', 'SK', 'SA'])
        s.evaluateHand()
        self.assertEqual(s.category, 2)

    def test_has_straight_high_and_low_ace(self):
        s = ShortHand(['HA', 'S6', 'ST', 'SJ', 'HQ', 'DK', 'SA'])
        s.evaluateHand()
        self.assertEqual(s.category, 4)

    def test_has_straight_high_ace(self):
        s = ShortHand(['H6', 'S6', 'ST', 'SJ', 'HQ', 'DK', 'SA'])
        s.evaluateHand()

    def test_has_straight_low_ace(self):
        s = ShortHand(['HA', 'S6', 'S7', 'S8', 'H9', 'DK', 'HK'])
        s.evaluateHand()
        self.assertEqual(s.category, 4)

    def test_has_straight_flush(self):
        s = ShortHand(['SA', 'S6', 'ST', 'SJ', 'SQ', 'SK', 'SA'])
        s.evaluateHand()
        self.assertEqual(s.category, 9)
