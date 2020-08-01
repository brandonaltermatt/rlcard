import json
import os
import numpy as np

import rlcard
from rlcard.envs import Env
from rlcard.games.limitholdem import Game

from rlcard.envs._limitholdem_infoset_encoders import LimitHoldemInfosetEncoder, NoFlushEncoder

class LimitholdemEnv(Env):
    ''' Limitholdem Environment
    '''
    INFOSET_ENCODERS = {
        'default': LimitHoldemInfosetEncoder(),
        'no-flush': NoFlushEncoder(),
    }
    GAME_CLASS = Game

    def __init__(self, config):
        ''' Initialize the Limitholdem environment

            config (dict): A config dictionary. An addition to the fields mentioned in env.__init__ there is:
                player_infoset_encoders (array of length 2): A string array of infoset encoder names, where each index
                    represents the player id of the player who gets said infoset encoder.
                    I.E. ['default', 'no-flush']
                    player 0 obs is encoded by the 'default' infoset encoding scheme
                    player 1 obs is encoded by the 'no-flush' infoset encoding scheme
        '''
        self.name = 'limit-holdem'
        if 'raise_num' in config:
            self.game = self.GAME_CLASS(allowed_raises=config['raise_num'])
        else:
            self.game = self.GAME_CLASS()
        config['record_action'] = True  # LimitHoldemInfosetEncoder requires details on bets
        self.player_infoset_encoders = []
        self._init_infoset_encoders(config)
        super().__init__(config)
        self.actions = ['call', 'raise', 'fold', 'check']

    def _init_infoset_encoders(self, config):
        if 'player_infoset_encoders' in config.keys():
            if len(config['player_infoset_encoders']) != 2:
                raise ValueError("Config item \'player_infoset_encoders\' should be an array of length 2")
            self.player_infoset_encoders.append(self.INFOSET_ENCODERS[config['player_infoset_encoders'][0]])
            self.player_infoset_encoders.append(self.INFOSET_ENCODERS[config['player_infoset_encoders'][1]])
        else:
            default = self.INFOSET_ENCODERS['default']
            self.player_infoset_encoders = [default, default]

    def _get_legal_actions(self):
        ''' Get all leagal actions

        Returns:
            encoded_action_list (list): return encoded legal action list (from str to int)
        '''
        return self.game.get_legal_actions()

    def _extract_state(self, state):
        ''' Extract the state representation from state dictionary for agent

        Args:
            state (dict): Original state from the game

        Returns:
            observation (list): combine the player's score and dealer's observable score for observation
        '''
        extracted_state = {}

        legal_actions = [self.actions.index(a) for a in state['legal_actions']]
        extracted_state['legal_actions'] = legal_actions
        infoset_encoder = self.player_infoset_encoders[state['player_id']]
        extracted_state['obs'] = infoset_encoder.encode(state, self.action_recorder)

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

    def get_state_shape(self, player_id):
        ''' Gets the state shape of the infoset encoder being used by player_id
        '''
        return self.player_infoset_encoders[player_id].state_shape
