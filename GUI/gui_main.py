import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
import GUI.project_parser as parser
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import rlcard
from rlcard.agents import RandomAgent
from rlcard.agents.one_look_agent import OneLookAgent
from rlcard.utils import set_global_seed, tournament

envName = ""
agentName = ""
againstAgentName = ""

def setGame(game):
    envName = game
    gameString.set("Game: " + envName + "\n\n")
def setAgent(agent):
    agentName = agent
    agentString.set("Main Agent: " + agentName + "\n\n")
def setAgainstAgent(againstAgent):
    againstAgentName = againstAgent
    againstAgentString.set("Against Agents: " + againstAgentName)


# Create placeholder for our plot that will be generated below
root = tk.Tk()

fig, ax = plt.subplots()
fig.suptitle("Rewards - 50 games played")
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(column=0,row=4, columnspan=2)

fig2, ax2 = plt.subplots()
fig2.suptitle("Accumulative rewards")
canvas2 = FigureCanvasTkAgg(fig2, master=root)
canvas2.get_tk_widget().grid(column=2,row=4)

# List the game modes
gameListBox = tk.Listbox(root)
gamesList = parser.getGames()
for game in gamesList:
    gameListBox.insert(tk.END, game)

gameListBox.grid(column=0,row=1)
tk.Button(root, text="Pick A Game", command= lambda: setGame(gameListBox.get(gameListBox.curselection()))).grid(column=0,row=2)

# List the agent options
agentListBox = tk.Listbox(root)
agentsList = parser.getAgents()
agentsNames = parser.getAgentNames(agentsList)
for name in agentsList:
    agentListBox.insert(tk.END, name)

agentListBox.grid(column=2,row=1)
tk.Button(root, text="PickMainAgent", command= lambda: setAgent(agentListBox.get(agentListBox.curselection()))).grid(column=2,row=2)
tk.Button(root, text="AddAgainstAgents", command= lambda: setAgainstAgent(agentListBox.get(agentListBox.curselection()))).grid(column=2,row=3)

# Display the information about the current game
gameString = tk.StringVar()
agentString = tk.StringVar()
againstAgentString = tk.StringVar()

gameLabel = tk.Label(root, textvariable=gameString)
agentLabel = tk.Label(root, textvariable=agentString)
againstAgentLabel = tk.Label(root, textvariable=againstAgentString)

gameLabel.grid(column=3,row=2)
agentLabel.grid(column=3, row=2)
againstAgentLabel.grid(column=3, row=2)


# Set up agents and enviorments
# Todo: Pull this information from unser input
baseEnv = rlcard.make('limit-holdem')
agentRando = RandomAgent(action_num=baseEnv.action_num)
agentOneLook = OneLookAgent(action_num=baseEnv.action_num)

mainAgent = agentOneLook
mainAgentName = "One Look"
otherAgents = [agentRando, agentRando]
otherAgentsName = ["Agent Random 1", "Agent Random 2"]

# Create a new game for each agent we are comparing agaisnt
envs = []
for agent in otherAgents:
    env = rlcard.make('limit-holdem')
    env.set_agents([mainAgent, agent])
    envs.append(env)
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

tk.Button(root, text="Start Game", command=startGame).grid(column=3,row=1)

root.mainloop()