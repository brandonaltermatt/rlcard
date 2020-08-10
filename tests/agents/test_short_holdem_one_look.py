import unittest
import rlcard
from rlcard.agents import RandomAgent
from rlcard.agents.one_look_agent import OneLookAgent, MODES
from rlcard.utils import set_global_seed, tournament

class TestOneLookShortHoldem(unittest.TestCase):

    def test_policy(self):
        actions = list(MODES[0].keys())
        weights = OneLookAgent.getPolicy(actions, ["DA", "HA"])
        self.assertTrue(weights == MODES[2])
        weights = OneLookAgent.getPolicy(actions, ["D8", "H7"])
        self.assertTrue(weights == MODES[1])
        weights = OneLookAgent.getPolicy(actions, ["D6", "H6"])
        self.assertTrue(weights == MODES[1])

    def test_save_and_load(self):
        env = rlcard.make('short-limit-holdem', config={'seed': 0})
        agentRando = RandomAgent(action_num=env.action_num)
        agentOneLook = OneLookAgent()
        env.set_agents([agentRando, agentOneLook])

        # Test
        result = tournament(env, 1000)
        self.assertTrue(result[1] > .2)

if __name__ == '__main__':
    unittest.main()

