import unittest

from rlcard.games.shortlimitholdem.utils import ShortHand

class TestShortLimitHoldemUtils(unittest.TestCase):
    ''' ShortLimitHoldem is not much different from regular LimitHoldem. However, in LimitHoldem,
    aces only count as a high card, while they count as a low and high card in Short.
    Because of this, the majority of these tests make sure this works.
    '''
    def test_ace_is_high_card(self):
        s = ShortHand(['HA', 'HT', 'H7', 'S8', 'S9', 'SK', 'SQ'])
        s.evaluateHand()
        self.assertEqual(s.category, 1)

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
