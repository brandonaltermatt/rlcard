import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def setAgent():
    pass
def setAgainstAgent():
    pass

import rlcard
from rlcard.agents import RandomAgent
from rlcard.agents.one_look_agent import OneLookAgent
from rlcard.utils import set_global_seed, tournament

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

agentList = tk.Listbox(root)
for item in ["One Look", "Random"]:
    agentList.insert(tk.END, item)
agentList.grid(column=0,row=1)
tk.Button(root, text="PickMainAgent", command=setAgent).grid(column=0,row=2)
tk.Button(root, text="AddAgainstAgents", command=setAgainstAgent).grid(column=0,row=3)

gameList = tk.Listbox(root)
for item in ["Limit Holdem", "Black Jack"]:
    gameList.insert(tk.END, item)
gameList.grid(column=2,row=1)
tk.Button(root, text="Pick A Game", command=setAgent).grid(column=2,row=2)

statusString = tk.StringVar()
statusLabel = tk.Label(root, textvariable=statusString)
statusString.set("Game: Limit Holdem\n\nMain Agent:\nOne Look\n\nAgainst Agents:\nRandom Agent\nRandom Agent")
statusLabel.grid(column=3,row=2)

root.mainloop()