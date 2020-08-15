import unittest
import rlcard
from rlcard.agents import RandomAgent
from rlcard.agents.short_limit_holdem_average_andy import ShortLimitholdemAverageAndy
from rlcard.utils import set_global_seed, tournament

class TestAverageAndyShortHoldem(unittest.TestCase):

    def test_handUtility(self):
        betterCards = ["DA", "HA"] # Pocket aces
        worseCards = ["H7", "CK"]  # Off-suit lower cards
        self.assertTrue(ShortLimitholdemAverageAndy.handUtility(betterCards) > ShortLimitholdemAverageAndy.handUtility(worseCards))

    def test_save_and_load(self):
        env = rlcard.make('short-limit-holdem', config={'seed': 0})
        agentRando = RandomAgent(action_num=env.action_num)
        agentAndy = ShortLimitholdemAverageAndy()
        env.set_agents([agentRando, agentAndy])

        # Agent takes too long to play, so really just making sure it does not
        # error out.
        result = tournament(env, 1)
        self.assertTrue(result[1] > .2)

if __name__ == '__main__':
    unittest.main()

