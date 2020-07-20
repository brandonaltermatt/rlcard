import json
import os
import numpy as np

import rlcard
from rlcard.envs import Env
from rlcard.games.limitholdem import Game

class LimitholdemEnv(Env):
    ''' Limitholdem Environment
    '''
    
    # Allow setting a custom Game class. This makes it easier to
    # extend limitholdem, such as in shortlimitholdem.
    GAME_CLASS = Game

    def __init__(self, config):
        ''' Initialize the Limitholdem environment
        '''
        self.name = 'limit-holdem'
        self.game = Game()
        super().__init__(config)
        self.actions = ['call', 'raise', 'fold', 'check']
        self.state_shape=[72]

        with open(os.path.join(rlcard.__path__[0], 'games/limitholdem/card2index.json'), 'r') as file:
            self.card2index = json.load(file)

    def _get_legal_actions(self):
        ''' Get all leagal actions

        Returns:
            encoded_action_list (list): return encoded legal action list (from str to int)
        '''
        return self.game.get_legal_actions()

    def _extract_state(self, state):
        ''' Extract the state representation from state dictionary for agent

        Note: Currently the use the hand cards and the public cards. TODO: encode the states

        Args:
            state (dict): Original state from the game

        Returns:
            observation (list): combine the player's score and dealer's observable score for observation
        '''
        extracted_state = {}

        legal_actions = [self.actions.index(a) for a in state['legal_actions']]
        extracted_state['legal_actions'] = legal_actions

        public_cards = state['public_cards']
        hand = state['hand']
        raise_nums = state['raise_nums']
        cards = public_cards + hand
        idx = [self.card2index[card] for card in cards]
        obs = np.zeros(72)
        obs[idx] = 1
        for i, num in enumerate(raise_nums):
            obs[52 + i * 5 + num] = 1
        extracted_state['obs'] = obs

        if self.allow_raw_data:
            extracted_state['raw_obs'] = state
            extracted_state['raw_legal_actions'] = [a for a in state['legal_actions']]
        if self.record_action:
            extracted_state['action_record'] = self.action_recorder
        return extracted_state

    def get_payoffs(self):
        ''' Get the payoff of a game

        Returns:
           payoffs (list): list of payoffs
        '''
        return self.game.get_payoffs()

    def _decode_action(self, action_id):
        ''' Decode the action for applying to the game

        Args:
            action id (int): action id

        Returns:
            action (str): action for the game
        '''
        legal_actions = self.game.get_legal_actions()
        if self.actions[action_id] not in legal_actions:
            if 'check' in legal_actions:
                return 'check'
            else:
                return 'fold'
        return self.actions[action_id]

    def _load_model(self):
        ''' Load pretrained/rule model

        Returns:
            model (Model): A Model object
        '''
        from rlcard import models
        return models.load('limit-holdem-rule-v1')

    def get_perfect_information(self):
        ''' Get the perfect information of the current state

        Returns:
            (dict): A dictionary of all the perfect information of the current state
        '''
        state = {}
        state['chips'] = [self.game.players[i].in_chips for i in range(self.player_num)]
        state['public_card'] = [c.get_index() for c in self.game.public_cards] if self.game.public_cards else None
        state['hand_cards'] = [[c.get_index() for c in self.game.players[i].hand] for i in range(self.player_num)]
        state['current_player'] = self.game.game_pointer
        state['legal_actions'] = self.game.get_legal_actions()
        return state

class LimitHoldemStateEncoder:
    RANK_ORDER = '23456789TJQKA'  # Allows for extension of No Limit Holdem

    def __init__(self):
        self.amount_of_ranks = len(self.RANK_ORDER)
        self.state_size = 25 + self.amount_of_ranks * 4
        self.state_shape = [self.state_size]
        self.encoded_vector = None

    def encode(self, state):
        self.encoded_vector = np.zeros(self.state_size)
        pass

    def _encode_cards(self, state):
        self._encode_card_ranks(state)
        pass

    def _encode_card_ranks(self, state):
        def encode_card_slot(cards, starting_index):
            for card in cards:
                rank = card[1]
                index = starting_index + self.RANK_ORDER.index(rank)
                self.encoded_vector[index] = 1

        hole_cards = state['hand']
        flop_cards = sorted(state['public_cards'][:3])
        turn_cards = state['public_cards'][3:4]
        river_cards = state['public_cards'][4:5]
        encode_card_slot(hole_cards, 25)
        encode_card_slot(flop_cards, (25 + self.amount_of_ranks))
        encode_card_slot(turn_cards, (25 + (self.amount_of_ranks * 2) + 1))
        encode_card_slot(river_cards, (25 + (self.amount_of_ranks * 3) + 1))
        # If there is a pair in the flop, set 1 if the pair is the higher of the two ranks
        if flop_cards and flop_cards[1][1] != flop_cards[0][1] and flop_cards[1][1] == flop_cards[2][1]:
            self.encoded_vector[25 + self.amount_of_ranks * 2] = 1

    def _encode_card_suits(self, state):
        hole_card_suits = [card[0] for card in state['hand']]
        community_card_suits = [card[0] for card in state['public_cards']]
        obs[37] = 1 if hole_card_suits[0] == hole_card_suits[1] else 0
        suits = ['SDCH']
        quads_suit = None
        trips_suit = None
        first_pair_suit = None
        second_pair_suit = None
        for suit in suits:
            suit_occurances = community_card_suits.count(suit)
            if suit_occurances == 4:
                quads_suit = suit
                community_card_suits = [s for s in community_card_suits if s != suit]
            if suit_occurances == 3:
                trips_suit = suit
                community_card_suits = [s for s in community_card_suits if s != suit]
            if suit_occurances == 2:
                if first_pair_suit is None:
                    first_pair_suit = suit
                else:
                    second_pair_suit = suit
                community_card_suits = [s for s in community_card_suits if s != suit]
        if first_pair_suit:
            obs[38] = 1
            obs[39] = 1 if first_pair_suit in hole_card_suits else 0
        if second_pair_suit:
            obs[40] = 1
            obs[41] = 1 if second_pair_suit in hole_card_suits else 0
        if trips_suit:
            obs[42] = 1
            obs[43] = 1 if trips_suit in hole_card_suits else 0
        if quads_suit:
            obs[44] = 1
            obs[45] = 1 if trips_suit in hole_card_suits else 0