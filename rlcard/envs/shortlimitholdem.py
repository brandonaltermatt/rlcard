from rlcard.envs.limitholdem import LimitholdemEnv, LimitHoldemInfosetEncoder
from rlcard.games.shortlimitholdem import Game

class ShortLimitHoldemInfosetEncoder(LimitHoldemInfosetEncoder):
    RANK_ORDER = '6789TJQKA'

class ShortlimitholdemEnv(LimitholdemEnv):
    ENCODER = ShortLimitHoldemInfosetEncoder()
    GAME_CLASS = Game