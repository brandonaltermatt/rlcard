from rlcard.envs.limitholdem import LimitholdemEnv
from rlcard.envs._limitholdem_infoset_encoders import LimitHoldemInfosetEncoder, NoFlushEncoder, NoHoleEncoder
from rlcard.games.shortlimitholdem import Game

class ShortLimitHoldemInfosetEncoder(LimitHoldemInfosetEncoder):
    RANK_ORDER = '6789TJQKA'

class ShortLimitHoldemNoFlushEncoder(NoFlushEncoder):
    RANK_ORDER = '6789TJQKA'

class ShortLimitHoldemNoHoleEncoder(NoHoleEncoder):
    RANK_ORDER = '6789TJQKA'

class ShortlimitholdemEnv(LimitholdemEnv):
    INFOSET_ENCODERS = {
        'default': ShortLimitHoldemInfosetEncoder(),
        'no-hole': ShortLimitHoldemNoHoleEncoder(),
        'no-flush': ShortLimitHoldemNoFlushEncoder(),
    }
    GAME_CLASS = Game
