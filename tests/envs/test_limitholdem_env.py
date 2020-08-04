import unittest
import numpy as np

import rlcard
from rlcard.envs._limitholdem_infoset_encoders import LimitHoldemInfosetEncoder, NoFlushEncoder, NoHoleEncoder
from rlcard.agents.random_agent import RandomAgent
from .determism_util import is_deterministic


class TestLimitholdemEnv(unittest.TestCase):

    def test_reset_and_extract_state(self):
        env = rlcard.make('limit-holdem')
        state, _ = env.reset()
        self.assertEqual(state['obs'].size, 78)
        for action in state['legal_actions']:
            self.assertLess(action, env.action_num)

    def test_is_deterministic(self):
        self.assertTrue(is_deterministic('limit-holdem'))

    def test_get_legal_actions(self):
        env = rlcard.make('limit-holdem')
        env.reset()
        legal_actions = env._get_legal_actions()
        for action in legal_actions:
            self.assertIn(action, env.actions)

    def test_decode_action(self):
        env = rlcard.make('limit-holdem')
        state, _ = env.reset()
        for action in state['legal_actions']:
            decoded = env._decode_action(action)
            self.assertIn(decoded, env.actions)

        decoded = env._decode_action(3)
        self.assertEqual(decoded, 'fold')

        env.step(0)
        decoded = env._decode_action(0)
        self.assertEqual(decoded, 'check')

    def test_step(self):
        env = rlcard.make('limit-holdem')
        state, player_id = env.reset()
        self.assertEqual(player_id, env.get_player_id())
        action = state['legal_actions'][0]
        _, player_id = env.step(action)
        self.assertEqual(player_id, env.get_player_id())

    def test_step_back(self):
        env = rlcard.make('limit-holdem', config={'allow_step_back':True})
        _, player_id = env.reset()
        env.step(0)
        _, back_player_id = env.step_back()
        self.assertEqual(player_id, back_player_id)
        self.assertEqual(env.step_back(), False)

        env = rlcard.make('limit-holdem')
        with self.assertRaises(Exception):
            env.step_back()

    def test_run(self):
        env = rlcard.make('limit-holdem')
        agents = [RandomAgent(env.action_num) for _ in range(env.player_num)]
        env.set_agents(agents)
        trajectories, payoffs = env.run(is_training=False)
        self.assertEqual(len(trajectories), 2)
        total = 0
        for payoff in payoffs:
            total += payoff
        self.assertEqual(total, 0)

    def test_get_perfect_information(self):
        env = rlcard.make('limit-holdem')
        _, player_id = env.reset()
        self.assertEqual(player_id, env.get_perfect_information()['current_player'])

    def test_differing_extract_state_obs(self):
        env = rlcard.make('limit-holdem', config={'player_infoset_encoders': ['default', 'no-flush']})
        sample_player0_state = {
            'player_id': 0,
            'raws_obs': [],
            'legal_actions': ['call', 'raise', 'fold'],
            'action_record': [],
            'hand': ['S3', 'S4'],
            'public_cards': [],
        }
        sample_player1_state = {
            'player_id': 1,
            'raws_obs': [],
            'legal_actions': ['call', 'raise', 'fold'],
            'action_record': [],
            'hand': ['S6', 'S5'],
            'public_cards': [],
        }
        player0_obs = env._extract_state(sample_player0_state)["obs"]
        player1_obs = env._extract_state(sample_player1_state)["obs"]
        self.assertEqual(len(player0_obs), 78)
        self.assertEqual(len(player1_obs), 63)

class TestLimitHoldemInfosetEncoder(unittest.TestCase):
    def test_encode_full_game(self):
        state = {'hand': ['S2', 'S3'], 'public_cards': ['S4', 'S5', 'S6', 'H3', 'H2'], 'player_id': 0}
        action_record = [
            [0, 'call'], [1, 'check'],
            [0, 'check'], [1, 'check'],
            [0, 'raise'], [1, 'call'],
            [0, 'raise'], [1, 'raise'], [0, 'raise'], [1, 'raise'], [0, 'call']
        ]
        e = LimitHoldemInfosetEncoder()
        expected_result = np.array([
            # Suits
            1.,
            1., 0.,
            0., 0.,
            1., 1.,
            0., 0.,
            # Bets
            0., 0., 0., 0.,
            0., 0., 0., 0.,
            0., 0., 1., 0.,
            1., 0., 0., 1.,
            # Cards
            1., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
            0., 0., 1., 1., 1., 0., 0., 0., 0., 0., 0., 0., 0.,
            0,
            0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
            1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.
        ])
        result = e.encode(state, action_record)
        self.assertTrue(np.array_equal(expected_result[0:9], result[0:9]))  # Suits encoded correctly
        self.assertTrue(np.array_equal(expected_result[9:25], result[9:25]))  # Bets encoded correctly
        self.assertTrue(np.array_equal(expected_result[25:], result[25:]))  # Ranks encoded correctly

    def test_encode_partial_game(self):
        state = {'hand': ['S2', 'S3'], 'public_cards': ['S4', 'S5', 'S6', 'H3'], 'player_id': 1}
        action_record = [
            [0, 'call'], [1, 'check'],
            [0, 'check'], [1, 'check'],
            [0, 'raise']
        ]
        e = LimitHoldemInfosetEncoder()
        expected_result = np.array([
            # Suits
            1.,
            0., 0.,
            0., 0.,
            1., 1.,
            0., 0.,
            # Bets
            0., 0., 0., 0.,
            0., 0., 0., 0.,
            0., 0., 1., 1.,
            0., 0., 0., 0.,
            # Cards
            1., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
            0., 0., 1., 1., 1., 0., 0., 0., 0., 0., 0., 0., 0.,
            0,
            0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
            0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.
        ])
        result = e.encode(state, action_record)
        self.assertTrue(np.array_equal(expected_result[0:9], result[0:9]))  # Suits encoded correctly
        self.assertTrue(np.array_equal(expected_result[9:25], result[9:25]))  # Bets encoded correctly
        self.assertTrue(np.array_equal(expected_result[25:], result[25:]))  # Ranks encoded correctly

    def test_encode_with_fold_action(self):
        e = LimitHoldemInfosetEncoder()
        state = {'hand': [], 'public_cards': [], 'player_id': 0}
        action_record = [
            [0, 'call'], [1, 'check'], 
            [0, 'check'], [1, 'check'],
            [0, 'raise'], [1, 'fold']
        ]
        expected_result = np.zeros(78)
        expected_result[19] = 1
        result = e.encode(state, action_record)
        self.assertTrue(np.array_equal(expected_result[9:25], result[9:25]))  # Bets encoded correctly

    def test_encode_suits(self):
        e = LimitHoldemInfosetEncoder()
        state = {'hand': ['D2', 'D3'], 'public_cards': ['S4', 'S5', 'S6', 'H3', 'H4'], 'player_id': 0}
        expected_result = np.zeros(78)
        expected_result[0] = 1
        expected_result[1] = 1
        expected_result[5] = 1
        result = e.encode(state, [])
        self.assertTrue(np.array_equal(expected_result[:9], result[:9]))  # Bets encoded correctly

        state = {'hand': ['H2', 'D3'], 'public_cards': ['S4', 'S5', 'D6', 'H3', 'H4'], 'player_id': 0}
        expected_result = np.zeros(78)
        expected_result[1] = 1
        expected_result[2] = 1
        expected_result[3] = 1
        result = e.encode(state, [])
        self.assertTrue(np.array_equal(expected_result[:9], result[:9]))  # Bets encoded correctly

class TestNoHoleEncoder(unittest.TestCase):
    def test_encoded_vector_has_no_hole_bits(self):
        state = {'hand': ['S2', 'S3'], 'public_cards': ['S4', 'S5', 'S6', 'H3'], 'player_id': 1}
        action_record = [
            [0, 'call'], [1, 'check'],
            [0, 'check'], [1, 'check'],
            [0, 'raise']
        ]
        e = NoHoleEncoder()
        expected_result = np.array([
            # Suits
            0.,
            0.,
            1.,
            0.,
            # Bets
            0., 0., 0., 0.,
            0., 0., 0., 0.,
            0., 0., 1., 1.,
            0., 0., 0., 0.,
            # Cards
            0., 0., 1., 1., 1., 0., 0., 0., 0., 0., 0., 0., 0.,
            0,
            0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
            0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.
        ])
        result = e.encode(state, action_record)
        self.assertTrue(np.array_equal(expected_result[0:4], result[0:4]))  # Suits encoded correctly
        self.assertTrue(np.array_equal(expected_result[9:25], result[9:25]))  # Bets encoded correctly
        self.assertTrue(np.array_equal(expected_result[25:], result[25:]))  # Ranks encoded correctly

# TODO Implement test cases
class TestNoFlushEncoder(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
