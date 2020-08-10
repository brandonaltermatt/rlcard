import inspect, sys
import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import rlcard.envs.registration as reg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import rlcard
from rlcard.agents import RandomAgent
from rlcard.utils import set_global_seed, tournament
import rlcard.games as games
import rlcard.agents as agents

# Finds the name of all the different games supported
# Returns list of strings
def getGames():
    return list(reg.registry.env_specs.keys())

# https://stackoverflow.com/questions/1796180/how-can-i-get-a-list-of-all-classes-within-current-module-in-python
# https://stackoverflow.com/questions/510972/getting-the-class-name-of-an-instance
# https://stackoverflow.com/questions/48000761/list-submodules-of-a-python-module
# Whoever found this deserves a medal
# Finds the class objects for all impleented agents.  Assumes all agents are in rlcard/agents folder
# Returns list of class objects
def getAgents():
    agentList = []
    agentFiles = dir(agents)
    # Some non-agent folders are provided, but they start with  "_"
    agentFiles = list(filter(lambda x : not x.startswith("_"), agentFiles))
    for agentFile in agentFiles:
        try:
            for _, obj in inspect.getmembers(sys.modules["rlcard.agents." + agentFile]):
                if inspect.isclass(obj):
                    agentList.append(obj)
        except BaseException as e:
            print("Error: " + str(e))
    return agentList

# https://stackoverflow.com/questions/2020014/get-fully-qualified-class-name-of-an-object-in-python
# Converts agent class to agent names for displaying
# returns list of string
def getAgentNames(agents):
    ret = []
    for agentClass in agents:
        ret.append(".".join([agentClass.__module__, agentClass.__name__]))
    return ret

# Binds a game with its players
def makeGame(agents, gameName):
    env = rlcard.make(gameName)
    agents = [a(action_num=env.action_num) for a in agents]
    env.set_agents(agents)
    return env

# Initialize the names of the environment and agents
games = getGames()
print(games)
agentOptions = getAgents()
print(agentOptions)
agentNames = getAgentNames(agentOptions)
print(agentNames)

envName = ""
selectedAgent = agentOptions[0]
agentName = ""
selectedAgainstAgent = agentOptions[0]
againstAgentName = ""

# Store the user selected game and agent in variables, update the status bar
def setGameName(selectedTuple):
    gameIndex = int(selectedTuple[0])
    envName = games[gameIndex]
    gameString.set("Game: " + envName + "\n")
def setAgentName(selectedTuple):
    agentIndex = int(selectedTuple[0])
    agentName = agentNames[agentIndex]
    agentString.set("Main Agent: " + agentName + "\n")
    selectedAgent = agentOptions[agentIndex]
def setAgainstAgentName(selectedTuple):
    agentIndex = int(selectedTuple[0])
    againstAgentName = agentNames[agentIndex]
    againstAgentString.set("Against Agents: " + againstAgentName)
    selectedAgainstAgent = agentOptions[agentIndex]


# Create placeholder for our plot that will be generated below
root = tk.Tk()

fig, ax = plt.subplots()
fig.suptitle("Rewards - 50 games played")
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(column=0,row=5, columnspan=2)

fig2, ax2 = plt.subplots()
fig2.suptitle("Accumulative rewards")
canvas2 = FigureCanvasTkAgg(fig2, master=root)
canvas2.get_tk_widget().grid(column=2,row=5)

# List the game modes
gameListBox = tk.Listbox(root, yscrollcommand=1)
for game in games:
    gameListBox.insert(tk.END, game)

gameListBox.grid(column=0,row=1)
tk.Button(root, text="Pick A Game", command= lambda: setGameName(gameListBox.curselection())).grid(column=0,row=2)

# List the agent options
agentListBox = tk.Listbox(root, width=40, yscrollcommand=1)
for item in agentNames:
    agentListBox.insert(tk.END, item)

agentListBox.grid(column=1,row=1)
tk.Button(root, text="PickMainAgent", command= lambda: setAgentName(agentListBox.curselection())).grid(column=1,row=2)
tk.Button(root, text="AddAgainstAgents", command= lambda: setAgainstAgentName(agentListBox.curselection())).grid(column=1,row=3)

# Display the information about the current game
gameString = tk.StringVar()
agentString = tk.StringVar()
againstAgentString = tk.StringVar()

gameLabel = tk.Label(root, textvariable=gameString)
agentLabel = tk.Label(root, textvariable=agentString)
againstAgentLabel = tk.Label(root, textvariable=againstAgentString)

gameString.set("Game: ")
agentString.set("Main Agent: ")
againstAgentString.set("Against Agents: ")

gameLabel.grid(column=2,row=1)
agentLabel.grid(column=2, row=2)
againstAgentLabel.grid(column=2, row=3)


# Set up agents and environments
# Todo: Pull this information from user input
mainAgent = agentOptions[-3]
mainAgentName = agentNames[-3]
otherAgents = [agentOptions[-3], agentOptions[-3]]
otherAgentsName = [agentNames[-3], agentNames[-3]]

# Create a new game for each agent we are comparing agaisnt
envs = []
for agent in otherAgents:
    envs.append(makeGame([mainAgent, agent], games[3]))

scores = [[] for _ in range(0,len(otherAgents))]
acumScores = [0 for _ in range(0,len(otherAgents))]



# Runs when graph is initially shown
def init():
    return ax,

# Runs every iteration. i Is the iteration count
def update(i):
    global acumScores
    ax.clear()
    for gameNum, env in enumerate(envs):
        newResults = tournament(env, 1)
        print(newResults)
        scores[gameNum].append(newResults)
        acumScores[gameNum] += newResults[1]
        line, = ax.plot(range(0,len(scores[gameNum])), [s[1] for s in scores[gameNum]])
        line.set_label(otherAgentsName[gameNum])
        ax.legend()
        
    line, = ax.plot(range(0,len(scores[0])), [0 for _ in scores[0]])
    line.set_label(mainAgentName)
    ax.legend()
    ax.grid('on')
    return ax,

# Runs when graph is initially shown
def init2():
    return ax2,

# Runs every iteration. i Is the iteration count
def update2(i):
    global acumScores
    ax2.clear()
    ax2.bar(otherAgentsName, acumScores)
    ax2.grid('on')
    return ax2,

# Puts updating the graph on a loop
def startGame():
    aniLineChart = FuncAnimation(fig, update, frames=range(0,10000), init_func=init, blit=True)
    aniLineChart = FuncAnimation(fig2, update2, frames=range(0,10000), init_func=init2, blit=True)

def setAgent():
    pass
def setAgainstAgent():
    pass


tk.Button(root, text="Start Game", command=startGame).grid(column=3,row=1)

root.mainloop()