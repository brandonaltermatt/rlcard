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

class LimitHoldemInfosetEncoder:
    RANK_ORDER = '23456789TJQKA'  # Allows for extension of No Limit Holdem

    def __init__(self):
        self.amount_of_ranks = len(self.RANK_ORDER)
        self.state_size = 25 + self.amount_of_ranks * 4
        self.state_shape = [self.state_size]
        self._encoded_vector = None

    def encode(self, player_state, action_record):
        '''
            Encodes the player state and action record into a binary list info set.
            Refer to the following post for more information:
            https://github.com/jake-bickle/rlcard/issues/11#issuecomment-661328769

            Args:
                player_state (dict): The dict returned by player.get_state()
                action_record (2D array): An array of actions, where an action is an array [player_id, action_string]

            Returns:
                A binary list of the encoded info set
        '''
        self._encoded_vector = np.zeros(self.state_size)
        self._encode_cards(player_state)
        self._encode_bets(action_record)
        return self._encoded_vector

    def _encode_cards(self, player_state):
        self._encode_card_ranks(player_state)
        self._encode_card_suits(player_state)

    def _encode_card_ranks(self, player_state):
        def encode_round_ranks(cards, starting_index):
            for card in cards:
                rank = card[1]
                index = starting_index + self.RANK_ORDER.index(rank)
                if index is not None:
                    self._encoded_vector[index] = 1

        hole_cards = player_state['hand']
        flop_cards = sorted(player_state['public_cards'][:3])
        turn_cards = player_state['public_cards'][3:4]
        river_cards = player_state['public_cards'][4:5]
        encode_round_ranks(hole_cards, 25)
        encode_round_ranks(flop_cards, (25 + self.amount_of_ranks))
        encode_round_ranks(turn_cards, (25 + (self.amount_of_ranks * 2) + 1))
        encode_round_ranks(river_cards, (25 + (self.amount_of_ranks * 3) + 1))
        # If there is a pair in the flop, set 1 if the pair is the higher of the two ranks
        if flop_cards and flop_cards[1][1] != flop_cards[0][1] and flop_cards[1][1] == flop_cards[2][1]:
            self._encoded_vector[25 + self.amount_of_ranks * 2] = 1

    def _encode_card_suits(self, player_state):
        hole_card_suits = [card[0] for card in player_state['hand']]
        community_card_suits = [card[0] for card in player_state['public_cards']]
        suits = 'SDCH'
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
        self._encoded_vector[0] = 1 if hole_card_suits[0] == hole_card_suits[1] else 0
        if first_pair_suit:
            self._encoded_vector[1] = 1
            self._encoded_vector[2] = 1 if first_pair_suit in hole_card_suits else 0
        if second_pair_suit:
            self._encoded_vector[3] = 1
            self._encoded_vector[4] = 1 if second_pair_suit in hole_card_suits else 0
        if trips_suit:
            self._encoded_vector[5] = 1
            self._encoded_vector[6] = 1 if trips_suit in hole_card_suits else 0
        if quads_suit:
            self._encoded_vector[7] = 1
            self._encoded_vector[8] = 1 if trips_suit in hole_card_suits else 0
        
    def _encode_bets(self, action_record):
        for round_action in self._infer_actions(action_record):
            round_number = round_action[0]
            number_of_bets = round_action[1]
            number_of_bets_binary = [int(x) for x in bin(number_of_bets)[2:]]  # Thanks to mgilson @ https://stackoverflow.com/a/13557953/9041692
            player_id_of_final_action = round_action[2]
            index_offset = 9 + (round_number * 3)
            self._encoded_vector[index_offset] = number_of_bets_binary[0]
            self._encoded_vector[index_offset + 1] = number_of_bets_binary[1]
            self._encoded_vector[index_offset + 2] = player_id_of_final_action

    @staticmethod
    def _infer_actions(action_record):
        # While action_record doesn't state when a new round of betting starts,
        # given the 2-player structure of the game this can be inferred.
        # Read the following post for more information:
        # https://github.com/jake-bickle/rlcard/issues/11#issuecomment-660538937
        round_actions = []
        new_round = True
        current_round = 0
        current_amount_of_bets = 0
        for action in action_record:
            if action[1] == 'raise':
                current_amount_of_bets += 1
            if action[1] == 'check' or action[1] == 'call':
                if new_round:
                    new_round = False
                else:
                    round = [current_round, current_amount_of_bets, action[0]]
                    current_round += 1
                    current_amount_of_bets = 0
        return round_actions
