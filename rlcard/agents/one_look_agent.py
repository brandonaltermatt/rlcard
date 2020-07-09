import numpy as np
from rlcard.agents import RandomAgent
from rlcard.utils import rank2int

MODES = []
MODES.append({"fold" : 8, "check" : 5, "call" : 2, "raise" : 1})# conservative
MODES.append({"fold" : 1, "check" : 1, "call" : 1, "raise" : 1})# neutral
MODES.append({"fold" : 1, "check" : 3, "call" : 2, "raise" : 8})# agressive

class OneLookAgent(RandomAgent):
    ''' Agent looks at his card to start the game, then never looks at the board
    '''
    def __init__(self, action_num):
        ''' Initilize the random agent

        Args:
            action_num (int): The size of the ouput action space
        '''
        self.use_raw = True
        self.action_num = action_num
        
    @staticmethod
    def step(state):
        ''' Based on purely the cards in the player's hand, they will be more likely to make an action.

        Args:
            state (dict): An dictionary that represents the current state

        Returns:
            action (int): The action predicted (randomly chosen) by the random agent
        '''
        # Figureout how good the hand is just based on card ranks
        cardScore = 0
        for card in state['raw_obs']['hand']:
            cardScore += rank2int(card[1])
        
        # Decide play style based on our hand
        mode = 2
        if cardScore < 8:
            mode = 0
        elif cardScore < 16:
            mode = 1
        
        # Pick an action depending on our play style
        actions = state['raw_obs']['legal_actions']
        weights = [MODES[mode][action] for action in actions]  
        scaler = 1/sum(weights)
        probabilities = [p * scaler for p in weights]  
        return np.random.choice(actions, p=probabilities)
