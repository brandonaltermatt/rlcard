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

    @ staticmethod    
    def getPolicy(self, actions, hand):
        ''' Based on purely the cards in the player's hand, they will be more likely to make an action.

        Args:
            actions (list[string]): name of actions player can take
            hand (list[string]): Player's hole cards

        Returns:
            probablities (list[float]): odds of choosing an action
        '''       
        # Figureout how good the hand is just based on card ranks
        cardScore = 0
        for card in hand:
            cardScore += rank2int(card[1])
        
        # Decide play style based on our hand
        mode = 2
        if cardScore < 8:
            mode = 0
        elif cardScore < 16:
            mode = 1
        
        # Decide play style based on hand
        weights = [MODES[mode][action] for action in actions]  
        scaler = 1/sum(weights)
        return [p * scaler for p in weights] 

    @staticmethod
    def step(state):
        ''' Player will pick a play style purely based on hards in hand

        Args:
            state (dict): An dictionary that represents the current state

        Returns:
            action (string): The action predicted (based on hand) by the random agent
        '''
        actions = state['raw_obs']['legal_actions']
        hand = state['raw_obs']['hand']
        probabilites = OneLookAgent.getPolicy(state, actions, hand)
        return np.random.choice(actions, p=probabilites)
