from rlcard.envs.limitholdem import LimitholdemEnv, LimitHoldemInfosetEncoder, MiniEncoder
from rlcard.games.shortlimitholdem import Game

class ShortLimitHoldemInfosetEncoder(LimitHoldemInfosetEncoder):
    RANK_ORDER = '6789TJQKA'
    
class MiniShortEncoder(MiniEncoder):
    RANK_ORDER = '6789TJQKA'    

class ShortlimitholdemEnv(LimitholdemEnv):
    ENCODER = MiniShortEncoder()
    GAME_CLASS = Game
