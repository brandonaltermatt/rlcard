from rlcard.envs.limitholdem import LimitholdemEnv
import rlcard.envs._shortlimitholdem_infoset_encoders as encoders
from rlcard.games.shortlimitholdem import Game

class ShortlimitholdemEnv(LimitholdemEnv):
    INFOSET_ENCODERS = {
        'default': encoders.ShortLimitHoldemInfosetEncoder(),
        'old-encoder': encoders.OldShortLimitHoldemInfosetEncoder(),
        'no-hole': encoders.ShortLimitHoldemNoHoleEncoder(),
        'no-flush': encoders.ShortLimitHoldemNoFlushEncoder(),
    }
    GAME_CLASS = Game
      