''' Limit Hold 'em rule model
'''
import rlcard
from rlcard.models.model import Model
from rlcard.agents.one_look_agent import OneLookAgent
from rlcard.models.limitholdem_rule_models import LimitholdemRuleModelV1 

class OneLookModelShortHoldem(LimitholdemRuleModelV1):
    ''' Limitholdem Rule Model version 1
    '''

    def __init__(self):
        ''' Load pretrained model
        '''
        self.game = "short-limit-holdem"
        env = rlcard.make(self.game)

        rule_agent = OneLookAgent()
        self.rule_agents = [rule_agent for _ in range(env.player_num)]