''' Limit Hold 'em rule model
'''
import rlcard, random, multiprocessing, time
from rlcard.agents import RandomAgent
from rlcard.core import Card
from rlcard.utils import tournament, rank2int, init_short_deck, get_random_cards, take_out_cards
from itertools import combinations
from rlcard.games.shortlimitholdem.utils import ShortHand

WINNING_ACTIONS = ['raise', 'call']
LOSING_ACTIONS = ['check', 'fold']

class LimitholdemHeuristic(RandomAgent):
    ''' Limit Heuristic
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
        utility = LimitholdemHeuristic.handUtility(hand + public_cards)

        # Play agressively if we have a better than average hand
        actions = WINNING_ACTIONS
        if len(public_cards) == 0 and utility <3.33:
            actions = LOSING_ACTIONS
        elif len(public_cards) > 0:
            otherUtility = LimitholdemHeuristic.handUtility(public_cards)
            if otherUtility > utility:  
                actions = LOSING_ACTIONS

        return list(filter(lambda a: a in legal_actions, actions))[0]

    def eval_step(self, state):
        ''' Step for evaluation. The same to step
        '''
        return self.step(state), []

    @staticmethod
    def handRanker(cards):
        score = 0
        score += max(map(lambda x: rank2int(x[1]), cards))/14
        return score

    @staticmethod
    def handUtility(cards):
        # remove availabe hand cards from a full deck
        fullDeck = init_short_deck()
        assert(len(fullDeck) == 36)
        for card in [Card(c[0], c[1]) for c in cards]:
            fullDeck.remove(card)
        if len(fullDeck) != 36 - len(cards):
            print(list(map(lambda card: card.suit + card.rank, fullDeck)))
            print(len(fullDeck))
            assert(False)

        # Generate all possilbe end hands the player could have
        allHands = LimitholdemHeuristic.get_all_hands(7-len(cards), fullDeck)
        allHands = [[card.suit + card.rank for card in hand] for hand in allHands]
        allHands = [cards + x for x in allHands]

        # Calculate the average utility of all possible hands
        pool = multiprocessing.Pool(multiprocessing.cpu_count())
        utility = sum(pool.map(LimitholdemHeuristic.evalHand, allHands))
        pool.close()
        # utility = sum(map(LimitholdemHeuristic.evalHand, allHands))
        return utility / len(allHands)

    @staticmethod
    def evalHand(hand):
        sh = ShortHand(hand)
        sh.evaluateHand()
        return sh.category

    @staticmethod
    def getAverageHandUtilityPreFlop(rounds):
        totalUtil = 0
        for _ in range(rounds):
            fullDeck = init_short_deck()
            hand, _ = get_random_cards(fullDeck, 2)
            handStr = [card.suit + card.rank for card in hand]
            totalUtil += LimitholdemHeuristic.handUtility(handStr)
        return totalUtil / rounds

    @staticmethod
    def get_all_hands(numCards, deck):
        return list(combinations(deck, numCards))

if __name__ == "__main__":
    start = time.time()
    env = rlcard.make('short-limit-holdem', config={'seed': 0})
    # Set up agents
    agentRando = RandomAgent(action_num=env.action_num)
    agentOneLook = LimitholdemHeuristic(action_num=env.action_num)
    env.set_agents([agentRando, agentOneLook])

    # Test
    result = tournament(env, 10)
    print(result)
    print(time.time() - start)
    assert(result[1] > .5)

    #print(LimitholdemHeuristic.getAverageHandUtilityPreFlop(10))
    
