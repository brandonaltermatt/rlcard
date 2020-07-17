from rlcard.games.limitholdem import Dealer
from rlcard.utils.utils import init_short_deck

class ShortLimitHoldemDealer(Dealer):
    def __init__(self, np_random):
        super().__init__(np_random)
        self.deck = init_short_deck()
        self.shuffle()
