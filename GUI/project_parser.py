import rlcard.games as games
import rlcard.agents as agents

# https://stackoverflow.com/questions/48000761/list-submodules-of-a-python-module
# Whoever found this deserves a medal
def getGames():
    return dir(games)

def getAgents():
    return dir(agents)

games = getGames()
print(games)
agents = getAgents()
print(agents)