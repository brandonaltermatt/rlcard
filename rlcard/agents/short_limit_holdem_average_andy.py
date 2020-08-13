''' Limit Hold 'em rule model
'''
import rlcard, random, multiprocessing, time
from rlcard.agents.one_look_agent import OneLookAgent
from rlcard.core import Card
from rlcard.utils import tournament, rank2int, init_short_deck, get_random_cards, take_out_cards
from itertools import combinations
from rlcard.games.shortlimitholdem.utils import ShortHand

WINNING_ACTIONS = ['raise', 'call']
LOSING_ACTIONS = ['check', 'fold']

class ShortLimitholdemAverageAndy(object):
    ''' Agent decides to play more or less agressively based on
        if the agent's cards are "better than average".  The agent
        takes the average utility of all possible hands the agent
        could have.
    '''

    def __init__(self):
        ''' Implementation is stateless, but could benefit from some
            caching to speed up implementation
        '''
        self.use_raw = True

    @staticmethod
    def step(state):
        ''' Plays if player's cards are "better" than average, becasuse
            it only knows how to play heads up.
        Args:
            state (dict): Raw state from the game

        Returns:
            action (str): Predicted action
        '''
        # Parse state
        legal_actions = state['raw_legal_actions']
        state = state['raw_obs']
        hand = state['hand']
        public_cards = state['public_cards']

        # Figureout how "good" our hand is
        utility = ShortLimitholdemAverageAndy.handUtility(hand + public_cards)

        # Play agressively if we have a better than average hand
        actions = WINNING_ACTIONS

        # All possible hands is too large to fully calculate in real time
        # on a normal desktop PC, 3.33 was emperically decided as a "average"
        # preflop hand.  See getAverageHandUtilityPreFlop for how this value
        # was decided
        if len(public_cards) == 0 and utility <3.33:
            actions = LOSING_ACTIONS
        
        # Decide if our hand is better than the average utility of just
        # the public cards.
        elif len(public_cards) > 0:
            otherUtility = ShortLimitholdemAverageAndy.handUtility(public_cards)
            if otherUtility > utility:  
                actions = LOSING_ACTIONS

        return list(filter(lambda a: a in legal_actions, actions))[0]

    def eval_step(self, state):
        ''' No randomness thrown in, so this is the same as the step function
        '''
        return self.step(state), []

    @staticmethod
    def handUtility(cards):
        ''' Decidse the "goodness" of a given hand.
        Args:
            cards (array of string): Two character formatted the same the game state

        Returns:
            utility (float): 1.0-9.0
        '''
        # remove availabe hand cards from a full deck
        fullDeck = init_short_deck()
        for card in [Card(c[0], c[1]) for c in cards]:
            fullDeck.remove(card)

        # Generate all possilbe end hands the player could have
        allHands = ShortLimitholdemAverageAndy.get_all_hands(7-len(cards), fullDeck)
        allHands = [[card.suit + card.rank for card in hand] for hand in allHands]
        allHands = [cards + x for x in allHands]

        # Calculate the average utility of all possible hands by using up all
        # of your CPU resources.  Can switch these lines with the one commented
        # out to do single CPU computation.
        pool = multiprocessing.Pool(multiprocessing.cpu_count())
        utility = sum(pool.map(ShortLimitholdemAverageAndy.evalHand, allHands))
        pool.close()
        # utility = sum(map(ShortLimitholdemAverageAndy.evalHand, allHands))
        return utility / len(allHands)

    @staticmethod
    def evalHand(hand):
        ''' Evaluates a full 7 card short holdem hand
        Args:
            hand (array of string): Two character formatted the same the game state

        Returns:
            rank (int): 1-9
        '''
        sh = ShortHand(hand)
        sh.evaluateHand()
        return sh.category

    @staticmethod
    def getAverageHandUtilityPreFlop(rounds):
        ''' Finding the average utility of all possible 7 card hands is takes too
            long to compute on a normal desktop, so this function was used to find
            the utility of x random hands to get an idea of what a "good" utility is
            before the flop happens.  The number found was ~3.3.
        Args:
            rounds (int): number of random hands to evaluate

        Returns:
            average utility (float): 1.0-9.0
        '''
        totalUtil = 0
        for _ in range(rounds):
            fullDeck = init_short_deck()
            hand, _ = get_random_cards(fullDeck, 2)
            handStr = [card.suit + card.rank for card in hand]
            totalUtil += ShortLimitholdemAverageAndy.handUtility(handStr)
        return totalUtil / rounds

    @staticmethod
    def get_all_hands(numCards, deck):
        ''' Generates all possible x number possible hands from a deck
        Args:
            numCards (int): how many cards each hand should have
            deck (list of Card): all possible cards to choose from

        Returns:
            hands (list of Card): generated hands
        '''
        return list(combinations(deck, numCards))

if __name__ == "__main__":
    start = time.time()
    env = rlcard.make('short-limit-holdem', config={'seed': 0})
    # Set up agents
    agentRando = OneLookAgent()
    agentOneLook = ShortLimitholdemAverageAndy()
    env.set_agents([agentRando, agentOneLook])

    # Test
    result = tournament(env, 10)
    print(result)
    print(time.time() - start)
    
