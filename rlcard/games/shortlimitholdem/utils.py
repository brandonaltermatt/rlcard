from rlcard.games.limitholdem.utils import Hand

class ShortHand(Hand):
    ''' Employs an alternative ranking system for a short hand game.
    Said ranks can be found here: https://www.pokernews.com/poker-rules/six-plus-hold-em.htm
    '''
    RANK_TO_STRING = {6: "6", 7: "7", 8: "8", 9: "9", 10: "T",
                      11: "J", 12: "Q", 13: "K", 14: "A"}
    RANK_LOOKUP = "A6789TJQKA"
    SUIT_LOOKUP = "SCDH"

    def evaluateHand(self):
        """
        Evaluate all the seven cards, get the best combination catagory
        And pick the best five cards (for comparing in case 2 hands have the same Category) .
        """
        if len(self.all_cards) != 7:
            raise Exception(
                "There must be 7 cards in a short hand, quit evaluation now! ")

        self._sort_cards()
        self.cards_by_rank, self.product = self._getcards_by_rank(
            self.all_cards)

        if self._has_straight_flush():
            self.category = 9
            #Straight Flush
        elif self._has_four():
            self.category = 8
            #Four of a Kind
            self.best_five = self._get_Four_of_a_kind_cards()
        elif self._has_flush():
            self.category = 7
            #Flush
            i = len(self.flush_cards)
            self.best_five = [card for card in self.flush_cards[i-5:i]]
        elif self._has_fullhouse():
            self.category = 6
            #Full house
            self.best_five = self._get_Fullhouse_cards()
        elif self._has_three():
            self.category = 5
            #Three of a Kind
            self.best_five = self._get_Three_of_a_kind_cards()
        elif self._has_straight(self.all_cards):
            self.category = 4
            #Straight
        elif self._has_two_pairs():
            self.category = 3
            #Two Pairs
            self.best_five = self._get_Two_Pair_cards()
        elif self._has_pair():
            self.category = 2
            #One Pair
            self.best_five = self._get_One_Pair_cards()
        elif self._has_high_card():
            self.category = 1
            #High Card
            self.best_five = self._get_High_cards()

    def _get_straight_cards(self, cards):
        '''
        Pick straight cards. Aces count as high and low.
        Returns:
            (list): the straight cards
        '''
        # Ensures that aces count for low and high cards
        highest_card = cards[-1]
        lowest_card = cards[0]
        if highest_card[1] == 'A':
            cards.insert(0, highest_card)
        elif lowest_card[1] == 'A':
            cards.append(lowest_card)

        i = len(cards)
        while (i - 5 >= 0):
            hand_to_check = ''.join(card[1] for card in cards[i-5:i])
            is_straight = self.RANK_LOOKUP.find(hand_to_check)
            if is_straight >= 0:
                five_cards = [card for card in cards[i-5:i]]
                return five_cards
            i -= 1
        return []
