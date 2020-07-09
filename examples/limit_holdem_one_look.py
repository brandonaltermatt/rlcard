import rlcard
from rlcard.agents import RandomAgent
from rlcard.agents.one_look_agent import OneLookAgent
from rlcard.utils import set_global_seed, tournament

# Make environment
env = rlcard.make('limit-holdem', config={'seed': 0})
episode_num = 5

# Set a global seed
set_global_seed(0)

# Set up agents
agentRando = RandomAgent(action_num=env.action_num)
agentOneLook = OneLookAgent(action_num=env.action_num)
env.set_agents([agentRando, agentOneLook])

print(tournament(env, 1000))