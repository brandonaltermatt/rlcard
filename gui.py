import inspect, sys
import tkinter as tk
from tkinter.filedialog import asksaveasfile 
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import rlcard
from rlcard.agents import RandomAgent
from rlcard.utils import set_global_seed, tournament
import rlcard.envs.registration as EnvReg
import rlcard.models.registration as ModelReg

# Global placehodlers. Will be initialized when start button is pressed
envs = None
scores = None
acumScores = None
gamesPlayed = None
fig = None
fig2 = None
ax = None
ax2 = None

# Global user selction placeholders
selectedAgent = None
selectedAgentName = None
envName = None
selectedAgainstAgents = []
selectedAgainstAgentNames = []

# Finds the name of all the different games supported
# Returns list of strings
def get_all_games():
    return list(EnvReg.registry.env_specs.keys())

def get_all_trained_agents(gameName=None):
    allAgents = []
    agentNames = []
    for agent in ModelReg.model_registry.model_specs.values():
        if gameName == None or agent.game == gameName:
            agentNames.append(agent.model_id)
            allAgents.append(agent.load().agents[0]) # assumes player is P1
    return (allAgents, agentNames)

# Binds a game with its players
def makeGame(players, gameName):
    env = rlcard.make(gameName)
    env.set_agents(players)
    return env

# Store the user selected game and agent in variables, update the status bar
def setGameName(selectedTuple):
    global envName
    gameIndex = int(selectedTuple[0])
    envName = games[gameIndex]
    gameString.set("Game: " + envName + "\n")

def setAgentName(selectedTuple):
    global selectedAgent, selectedAgentName
    agentIndex = int(selectedTuple[0])
    agentName = agentNames[agentIndex]
    agentString.set("Main Agent: " + agentName + "\n")
    selectedAgent = allAgents[agentIndex]
    selectedAgentName = agentNames[agentIndex]

def setAgainstAgentName(selectedTuple):
    global selectedAgainstAgents, selectedAgainstAgentNames
    agentIndex = int(selectedTuple[0])
    selectedAgainstAgents.append(allAgents[agentIndex])
    selectedAgainstAgentNames.append(agentNames[agentIndex])
    againstAgentString.set("Against Agents:\n" + "\n".join(selectedAgainstAgentNames))
    

# Puts updating the graph on a loop
def startGame():
    global scores, acumScores, envs, gamesPlayed, fig, fig2, ax, ax2
    envs = []
    for agent in selectedAgainstAgents:
        envs.append(makeGame([selectedAgent, agent], envName))
    scores = [[] for _ in enumerate(selectedAgainstAgents)]
    acumScores = [0 for _ in enumerate(selectedAgainstAgents)]
    gamesPlayed = [[] for _ in enumerate(selectedAgainstAgents)]

    fig = plt.figure()
    ax = plt.axes()
    fig.suptitle("Rewards - 50 games played")
    fig2 = plt.figure()
    ax2 = plt.axes()
    fig2.suptitle("Accumulative rewards")

    FuncAnimation(fig, update, init_func=init, blit=True, frames=200, interval=20)
    FuncAnimation(fig2, update2, init_func=init2, blit=True, frames=200, interval=20)
    plt.show()
# Saves test results
def saveRun():
    global gamesPlayed
    saveTypes = [("JSON Files", "*.json")]
    toSave = asksaveasfile(filetypes = saveTypes, defaultextension = saveTypes)
    toSave.write(str(gamesPlayed))
    toSave.close()

# Runs when graph is initially shown
def init():
    return ax,

# Runs every iteration. i Is the iteration count
def update(i):
    global acumScores
    ax.clear()
    for gameNum, env in enumerate(envs):

        gameData, newResults = env.run(is_training=False)
        scores[gameNum].append(newResults)
        gamesPlayed[gameNum].append(gameData)
        acumScores[gameNum] += newResults[1]

        line, = ax.plot(range(0,len(scores[gameNum])), [s[1] for s in scores[gameNum]])
        line.set_label(selectedAgainstAgentNames[gameNum])
        ax.legend()
        
    # Plotting other agent's rewards, so just a line of 0 for reference
    line, = ax.plot(range(0,len(scores[0])), [0 for _ in scores[0]])
    line.set_label(selectedAgentName)
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
    ax2.bar(selectedAgainstAgentNames, acumScores)
    ax2.grid('on')
    return ax2,


# Initialize the names of the environment and agents for menu creation
games = get_all_games()
(allAgents, agentNames) = get_all_trained_agents()

# Create placeholder for our plot that will be generated below
root = tk.Tk()

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

tk.Button(root, text="Start Game", command=startGame).grid(column=3,row=0)
tk.Button(root, text="Save Run", command=saveRun).grid(column=3,row=1)

root.mainloop()