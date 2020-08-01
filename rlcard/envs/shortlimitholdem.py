from rlcard.envs.limitholdem import LimitholdemEnv
from rlcard.envs._limitholdem_infoset_encoders import LimitHoldemInfosetEncoder, NoFlushEncoder
from rlcard.games.shortlimitholdem import Game

class ShortLimitHoldemInfosetEncoder(LimitHoldemInfosetEncoder):
    RANK_ORDER = '6789TJQKA'
    
class MiniShortEncoder(NoFlushEncoder):
    RANK_ORDER = '6789TJQKA'    

class ShortlimitholdemEnv(LimitholdemEnv):
    ENCODER = MiniShortEncoder()
    GAME_CLASS = Game
