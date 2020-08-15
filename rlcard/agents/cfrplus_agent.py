import numpy as np
from rlcard.agents.cfr_agent import CFRAgent

class CFRPlusAgent(CFRAgent):
    ''' 
        WARNING: WORK IN PROGRESS, PROBABLY BUGGY
        
        Modified CFRAgent ('vanilla' CFR) with various optimizations
        
        CFR+
        https://arxiv.org/abs/1407.5042
        
        DCFR
        https://arxiv.org/pdf/1809.04040.pdf
    '''
    
    ALPHA = 1.5
    BETA = 0
    GAMMA = 2
    ''' Parameters for Discounted CFR (DCFR)
    
        On updating each action's regret, on iteration t:
        - Accumulated positive regret is multiplied by:
            t ^ ALPHA / (t ^ ALPHA + 1)
            
        - Accumulated negative regret is multiplied by:
            t ^ BETA / (t ^ BETA+ 1)
            
        - Contribution to average policy is multiplied by:
            (t / t + 1) ^ GAMMA
            
        Default parameters (generally perform well in most games): 1.5, 0, 2
        
        Linear CFR (LCFR) is equivalent to DCFR(1,1,1)
        LCFR performs best in games with the potential for extremely large
        mistakes, such as no limit poker
        
        CFR+ is equivalent to DCFR(inf,-inf,2)
    '''
    
    TRAINING_DELAY = 0 
    ''' Complete this many iterations before beginning updates to the average 
    policy. Used in some CFR+ implementations. Generally not used with DCFR.
    '''
    
    def __init__(self, env, model_path='./cfr+_model'):
        super().__init__(env, model_path='./cfr+_model')

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
            
            
        # DCFR weight adjusting
            if self.regrets[obs][action] > 0:
                self.regrets[obs][action] *= (self.iteration ** self.ALPHA) / (self.iteration ** self.ALPHA + 1)
            else:
                self.regrets[obs][action] *= (self.iteration ** self.BETA) / (self.iteration ** self.BETA + 1)
            if self.TRAINING_DELAY <= self.iteration:
                self.average_policy[obs][action] += ((self.iteration / (self.iteration + 1)) ** 2) * player_prob * action_prob
            
            self.regrets[obs][action] += regret
            
            
        return state_utility
