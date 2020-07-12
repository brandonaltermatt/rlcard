import rlcard
from rlcard.agents import RandomAgent
from rlcard.agents.one_look_agent import OneLookAgent
from rlcard.utils import set_global_seed, tournament

env = rlcard.make('limit-holdem', config={'seed': 0})
set_global_seed(0)

# Set up agents
agentRando = RandomAgent(action_num=env.action_num)
agentOneLook = OneLookAgent(action_num=env.action_num)
env.set_agents([agentRando, agentOneLook])

# Test
result = tournament(env, 1000)
print(result)
assert(result[1] > .5)