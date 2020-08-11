''' Limit Hold 'em rule model
'''
import rlcard
from rlcard.models.model import Model
from rlcard.agents.random_agent import RandomAgent
from rlcard.models.limitholdem_rule_models import LimitholdemRuleModelV1 

class RandomModelBlackJack(LimitholdemRuleModelV1):
    ''' Limitholdem Rule Model version 1
    '''

    def __init__(self):
        ''' Load pretrained model
        '''
        self.game = "blackjack"
        env = rlcard.make(self.game)

        rule_agent = RandomAgent(env.action_num)
        self.rule_agents = [rule_agent for _ in range(env.player_num)]

class RandomModelDoudizhu(LimitholdemRuleModelV1):
    ''' Limitholdem Rule Model version 1
    '''

    def __init__(self):
        ''' Load pretrained model
        '''
        self.game = "doudizhu"
        env = rlcard.make(self.game)

        rule_agent = RandomAgent(env.action_num)
        self.rule_agents = [rule_agent for _ in range(env.player_num)]

class RandomModelShortLimitHoldem(LimitholdemRuleModelV1):
    ''' Limitholdem Rule Model version 1
    '''

    def __init__(self):
        ''' Load pretrained model
        '''
        self.game = "short-limit-holdem"
        env = rlcard.make(self.game)

        rule_agent = RandomAgent(env.action_num)
        self.rule_agents = [rule_agent for _ in range(env.player_num)]