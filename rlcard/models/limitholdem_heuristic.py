''' Limit Hold 'em rule model
'''
import rlcard
from rlcard.utils import init_54_deck, take_out_cards, rank2int, get_random_cards
from itertools import combinations

class LimitholdemHeuristic(object):
    ''' Limit Heuristic
    '''

    def __init__(self):
        self.use_raw = True

    @staticmethod
    def step(state):
        ''' Predict the action when given raw state. A simple rule-based AI.
        Args:
            state (dict): Raw state from the game

        Returns:
            action (str): Predicted action
        '''
        legal_actions = state['raw_legal_actions']
        state = state['raw_obs']
        hand = state['hand']
        public_cards = state['public_cards']
        return 'fold'

    def eval_step(self, state):
        ''' Step for evaluation. The same to step
        '''
        return self.step(state), []

    @staticmethod
    def eval_hand(cards):
        pass

    @staticmethod
    def get_all_hands(numCards, deck):
        return list(combinations(init_54_deck(), numCards))

    @staticmethod
    def handRanker(cards):
        ranks = map(lambda x: rank2int(x.rank), cards)
        return max(ranks)/14

    @staticmethod
    def handSorter(h1, h2):
        return LimitholdemHeuristic.handRanker(h1) - LimitholdemHeuristic.handRanker(h2)

if __name__ == "__main__":
    hand, deck = get_random_cards(init_54_deck(), 2)
    print(LimitholdemHeuristic.handRanker(hand))
    oppHands = LimitholdemHeuristic.get_all_hands(7, deck)
    print(len(oppHands))
    
