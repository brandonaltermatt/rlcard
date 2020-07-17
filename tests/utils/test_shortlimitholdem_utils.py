import unittest

from rlcard.games.shortlimitholdem.utils import ShortHand

class TestShortLimitHoldemUtils(unittest.TestCase):
    ''' ShortLimitHoldem is not much different from regular LimitHoldem. However, in LimitHoldem,
    aces only count as a high card, while they count as a low and high card in Short.
    Because of this, the majority of these tests make sure this works.
    '''
    def test_high_card_1(self):
        s = ShortHand(['H6', 'H7', 'H8', 'S9', 'SJ', 'SK', 'SQ'])
        s.evaluateHand()
        self.assertEqual(s.category, 1)

    def test_high_card_2(self):
        s = ShortHand(['H6', 'H7', 'C9', 'SJ', 'DQ', 'HK', 'SA'])
        s.evaluateHand()
        self.assertEqual(s.category, 1)        

    def test_has_pair(self):
        s = ShortHand(['HA', 'HT', 'H7', 'S8', 'S9', 'SK', 'SA'])
        s.evaluateHand()
        self.assertEqual(s.category, 2)
        
    def test_has_2_pair(self):
        s = ShortHand(['H6', 'HK', 'H7', 'S8', 'S9', 'SK', 'S6'])
        s.evaluateHand()
        self.assertEqual(s.category, 3)   

    def test_has_trips(self):
        s = ShortHand(['SK', 'S6', 'S7', 'S8', 'H9', 'DK', 'HK'])
        s.evaluateHand()
        self.assertEqual(s.category, 4)   

    def test_has_straight(self):
        s = ShortHand(['H6', 'S8', 'S9', 'SJ', 'HQ', 'DT', 'SA'])
        s.evaluateHand()
        self.assertEqual(s.category, 5)        

    def test_has_straight_high_and_low_ace(self):
        s = ShortHand(['HA', 'S6', 'ST', 'SJ', 'HQ', 'DK', 'SA'])
        s.evaluateHand()
        self.assertEqual(s.category, 5)

    def test_has_straight_high_ace(self):
        s = ShortHand(['H6', 'S6', 'ST', 'SJ', 'HQ', 'DK', 'SA'])
        s.evaluateHand()
        self.assertEqual(s.category, 5)

    def test_has_straight_low_ace(self):
        s = ShortHand(['HA', 'S6', 'S7', 'S8', 'H9', 'DK', 'HK'])
        s.evaluateHand()
        self.assertEqual(s.category, 5)

    def test_has_straight_with_pair(self):
        s = ShortHand(['HA', 'S6', 'S7', 'S8', 'H9', 'DK', 'HK'])
        s.evaluateHand()
        self.assertEqual(s.category, 5)      

    def test_has_straight_with_2_pair(self):
        s = ShortHand(['HA', 'S6', 'S7', 'S8', 'H9', 'D6', 'H7'])
        s.evaluateHand()
        self.assertEqual(s.category, 5)               

    def test_has_straight_with_trips(self):
        s = ShortHand(['HA', 'S6', 'S7', 'S8', 'H9', 'D6', 'H6'])
        s.evaluateHand()
        self.assertEqual(s.category, 5)          

    def test_has_fullhouse(self):
        s = ShortHand(['HA', 'SA', 'DA', 'S8', 'C8', 'D6', 'H9'])
        s.evaluateHand()
        self.assertEqual(s.category, 6)   
        
    def test_has_fullhouse_extra_pair(self):
        s = ShortHand(['HA', 'SA', 'DA', 'S8', 'C8', 'D6', 'H6'])
        s.evaluateHand()
        self.assertEqual(s.category, 6) 

    def test_has_flush_spades(self):
        s = ShortHand(['SA', 'SK', 'SQ', 'S9', 'S8', 'C7', 'C8'])
        s.evaluateHand()
        self.assertEqual(s.category, 7)           

    def test_has_flush_hearts(self):
        s = ShortHand(['HA', 'HK', 'HQ', 'H9', 'H8', 'C7', 'C8'])
        s.evaluateHand()
        self.assertEqual(s.category, 7)         
        
    def test_has_flush_diamonds(self):
        s = ShortHand(['DA', 'DK', 'DQ', 'D9', 'D8', 'C7', 'C8'])
        s.evaluateHand()
        self.assertEqual(s.category, 7)   

    def test_has_flush_clubs(self):
        s = ShortHand(['CA', 'CK', 'CQ', 'C9', 'C8', 'H7', 'S8'])
        s.evaluateHand()
        self.assertEqual(s.category, 7)                 

    def test_has_flush_7_cards(self):
        s = ShortHand(['HQ', 'HK', 'HJ', 'H9', 'H8', 'H7', 'H6'])
        s.evaluateHand()
        self.assertEqual(s.category, 7)      

    def test_has_flush_with_trips(self):
        s = ShortHand(['HQ', 'HK', 'HJ', 'H9', 'H8', 'CQ', 'SQ'])
        s.evaluateHand()
        self.assertEqual(s.category, 7)     

    def test_has_flush_with_straight(self):
        s = ShortHand(['HQ', 'HK', 'HJ', 'H9', 'H8', 'CT', 'DA'])
        s.evaluateHand()
        self.assertEqual(s.category, 7)   

    def test_has_quads(self):
        s = ShortHand(['HQ', 'CQ', 'DQ', 'SQ', 'H8', 'CT', 'DA'])
        s.evaluateHand()
        self.assertEqual(s.category, 8) 
        
    def test_has_quads_aces(self):
        s = ShortHand(['HA', 'CA', 'DA', 'SA', 'H8', 'CT', 'DK'])
        s.evaluateHand()
        self.assertEqual(s.category, 8)         

    def test_has_quads_with_trips(self):
        s = ShortHand(['HQ', 'CQ', 'DQ', 'SQ', 'H8', 'C8', 'S8'])
        s.evaluateHand()
        self.assertEqual(s.category, 8)          


    def test_has_straight_flush(self):
        s = ShortHand(['SA', 'S6', 'ST', 'SJ', 'SQ', 'SK', 'SA'])
        s.evaluateHand()
        self.assertEqual(s.category, 9)
      
    def test_has_straight_flush_low(self):
        s = ShortHand(['HA', 'S6', 'S7', 'S8', 'S9', 'SK', 'SA'])
        s.evaluateHand()
        self.assertEqual(s.category, 9)
   
