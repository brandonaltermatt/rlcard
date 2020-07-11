from rlcard.games.limitholdem.utils import Hand

class ShortHand(Hand):
    ''' Employs an alternative ranking system for a short hand game.
    Said ranks can be found here: https://www.pokernews.com/poker-rules/six-plus-hold-em.htm
    '''
    RANK_TO_STRING = {6: "6", 7: "7", 8: "8", 9: "9", 10: "T",
                      11: "J", 12: "Q", 13: "K", 14: "A"}
    RANK_LOOKUP = "6789TJQKA"

    def evaluateHand(self):
        """
        Evaluate all the seven cards, get the best combination catagory
        And pick the best five cards (for comparing in case 2 hands have the same Category) .
        """
        # Fullhouse and Flush categories are swapped
        super().evaluateHand()
        if self.category == 7:  # Fullhouse
            self.category = 6
        elif self.category == 6:  # Flush
            self.category = 7
