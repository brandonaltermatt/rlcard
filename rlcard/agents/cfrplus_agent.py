import numpy as np
import collections

import os
import pickle

from rlcard.utils.utils import *
from rlcard.agents.cfr_agent import CFRAgent

class CFRPlusAgent(CFRAgent):
    ''' Implement CFR+ algorithm
        Modified CFRAgent (vanilla CFR) with various optimizations
    '''
    
    TRAINING_DELAY = 0 
    ''' Complete this many iterations before beginning updates to the average policy
    '''

    def __init__(self, env, model_path='./cfrplus_model'):
        ''' Initilize Agent
        '''        
        super().__init__(env, model_path='./cfrplus_model')

    def traverse_tree(self, probs, player_id):
        ''' Traverse the game tree, update the regrets

        Args:
            probs: The reach probability of the current node
            player_id: The player to update the value

        Returns:
            state_utilities (list): The expected utilities for all the players
        '''
        if self.env.is_over():
            return self.env.get_payoffs()

        current_player = self.env.get_player_id()

        action_utilities = {}
        state_utility = np.zeros(self.env.player_num)
        obs, legal_actions = self.get_state(current_player)
        action_probs = self.action_probs(obs, legal_actions, self.policy)

        for action in legal_actions:
            action_prob = action_probs[action]
            new_probs = probs.copy()
            new_probs[current_player] *= action_prob

            # Keep traversing the child state
            self.env.step(action)
            utility = self.traverse_tree(new_probs, player_id)
            self.env.step_back()

            state_utility += action_prob * utility
            action_utilities[action] = utility

        if not current_player == player_id:
            return state_utility

        # If it is current player, we record the policy and compute regret
        player_prob = probs[current_player]
        counterfactual_prob = (np.prod(probs[:current_player]) *
                                np.prod(probs[current_player + 1:]))
        player_state_utility = state_utility[current_player]

        if obs not in self.regrets:
            self.regrets[obs] = np.zeros(self.env.action_num)
        if obs not in self.average_policy:
            self.average_policy[obs] = np.zeros(self.env.action_num)
        for action in legal_actions:
            action_prob = action_probs[action]
            regret = counterfactual_prob * (action_utilities[action][current_player]
                    - player_state_utility)
            self.regrets[obs][action] += regret
          
        #CFRPlus modifications
            if self.regrets[obs][action] < 0:
                self.regrets[obs][action] *= 0.5
            else:
                self.regrets[obs][action] *= (self.iteration ** 1.5) / (self.iteration ** 1.5 + 1)
            if TRAINING_DELAY <= self.iteration:
                self.average_policy[obs][action] += ((self.iteration ** 2) / (self.iteration ** 2 + 1)) * player_prob * action_prob
                       
        return state_utility