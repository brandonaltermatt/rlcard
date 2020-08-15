import numpy as np
from rlcard.agents import RandomAgent
from rlcard.utils import rank2int

# Adds weights to how often an action will be made
CONSERVATIVE_WEIGHTS = {"fold" : 8, "check" : 5, "call" : 2, "raise" : 1}
NEUTRIAL_WEIGHTS = {"fold" : 8, "check" : 5, "call" : 2, "raise" : 1}
AGRESSIVE_WEIGHTS = {"fold" : 1, "check" : 3, "call" : 2, "raise" : 8}
MODES = [CONSERVATIVE_WEIGHTS, NEUTRIAL_WEIGHTS, AGRESSIVE_WEIGHTS]

class OneLookAgent(object):
    ''' Agent looks at it's card to start the game, then never looks at the board
    '''
    def __init__(self):
        ''' Stateless implementation
        '''
        self.use_raw = True

    @ staticmethod    
    def getPolicy(actions, hand):
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
        if cardScore < 16:
            mode = 0
        elif cardScore < 21:
            mode = 1

        return MODES[mode]

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

        weights = OneLookAgent.getPolicy(actions, hand)
        probabilites = [weights[action] for action in actions]  
        scaler = 1/sum(probabilites)
        normProbs =  [p * scaler for p in probabilites] 
        return np.random.choice(actions, p=normProbs)

    def eval_step(self, state):
        ''' No randomness thrown in, so this is the same as the step function
        '''
        return self.step(state), []