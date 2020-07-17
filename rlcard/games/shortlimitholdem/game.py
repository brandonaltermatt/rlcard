from rlcard.games.limitholdem import Game
from rlcard.games.shortlimitholdem import Dealer
from rlcard.games.shortlimitholdem import Judger

class ShortLimitHoldemGame(Game):
    DEALER_CLASS = Dealer
    JUDGER_CLASS = Judger