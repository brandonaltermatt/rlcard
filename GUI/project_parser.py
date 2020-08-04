import sys, inspect
import rlcard.games as games
import rlcard.agents as agents
import rlcard.envs.registration as reg
from rlcard import make

def getGames():
    return list(reg.registry.env_specs.keys())

# https://stackoverflow.com/questions/1796180/how-can-i-get-a-list-of-all-classes-within-current-module-in-python
# https://stackoverflow.com/questions/510972/getting-the-class-name-of-an-instance
# https://stackoverflow.com/questions/48000761/list-submodules-of-a-python-module
# Whoever found this deserves a medal
def getAgents():
    agentList = []
    agentFiles = dir(agents)
    agentFiles = list(filter(lambda x : not x.startswith("_"), agentFiles))
    for agentFile in agentFiles:
        try:
            for name, obj in inspect.getmembers(sys.modules["rlcard.agents." + agentFile]):
                if inspect.isclass(obj):
                    agentList.append(obj)
        except BaseException as e:
            pass
    return agentList

# https://stackoverflow.com/questions/2020014/get-fully-qualified-class-name-of-an-object-in-python
def getAgentNames(agentClasses):
    ret = []
    for agentClass in agentClasses:
        ret.append(".".join([agentClass.__module__, agentClass.__name__]))
    return ret

def makeGame(agents, gameName):
    env = make(gameName)
    env.set_agents(agents)
    return env

# Display the lists of games and agents
# Weird bug: Uncommenting the code block below will prevent the agent list in the GUI from dynamically populating
"""
games = getGames()
print(games)
agents = getAgents()
agentNames = getAgentNames(agents)
print(agentNames)
#env = makeGame(agents[-6], games[3])
"""