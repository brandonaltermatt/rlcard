import numpy as np
import rlcard.envs._limitholdem_infoset_encoders as encoders

class ShortLimitHoldemInfosetEncoder:
    STATE_SIZE = 62
    STATE_SHAPE = [STATE_SIZE]
    BITS_TO_DELETE = [
        # These bits correspond to the ranks 2-5
        25, 26, 27, 28,
        38, 39, 40, 41,
        52, 53, 54, 55,
        65, 66, 67, 68
    ]

    def encode(self, *args, **kwargs):
        e = encoders.LimitHoldemInfosetEncoder()
        encoded_vector = e.encode(*args, **kwargs)
        return np.delete(encoded_vector, self.BITS_TO_DELETE)

class OldShortLimitHoldemInfosetEncoder:
    STATE_SIZE = 56
    STATE_SHAPE = [STATE_SIZE]
    BITS_TO_DELETE = [
        1, 2, 3, 4, 
        14, 15, 16, 17,
        27, 28, 29, 30,
        40, 41, 42, 43
    ]

    def encode(self, *args, **kwargs):
        e = encoders.OldLimitHoldemInfosetEncoder()
        encoded_vector = e.encode(*args, **kwargs)
        return np.delete(encoded_vector, self.BITS_TO_DELETE)

class ShortLimitHoldemNoFlushEncoder:
    STATE_SIZE = 47
    STATE_SHAPE = [STATE_SIZE]
    BITS_TO_DELETE = [
        1, 2, 3, 4,
        14, 15, 16, 17,
        28, 29, 30, 31,
        41, 42, 43, 44
    ]

    def encode(self, *args, **kwargs):
        e = encoders.NoFlushEncoder()
        encoded_vector = e.encode(*args, **kwargs)
        return np.delete(encoded_vector, self.BITS_TO_DELETE)

class ShortLimitHoldemNoHoleEncoder:
    STATE_SIZE = 48
    STATE_SHAPE = [STATE_SIZE]
    # These bits correspond to the ranks 2-5
    BITS_TO_DELETE = [
        20, 21, 22, 23,
        34, 35, 36, 37,
        47, 48, 49, 50
    ]

    def encode(self, *args, **kwargs):
        e = encoders.NoHoleEncoder()
        encoded_vector = e.encode(*args, **kwargs)
        return np.delete(encoded_vector, self.BITS_TO_DELETE)
