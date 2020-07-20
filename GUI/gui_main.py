import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Game:
    def __init__(self, importString, displayName):
        self.importString = importString
        self.displayName = displayName

class Agent:
    def __init__(self, importString, displayName):
        self.importString = importString
        self.displayName = displayName

class Contest:
    def __init__(self, game, agents):
        self.game = game
        self.agents = agents
        #self.env =

def getGames():
    importString = "TBD"
    displayName = "Holdem"
    return [Game(importString , displayName)]

def getAgents(game):
    importString = "TBD"
    displayName = "randomAgent"
    return [Agent(importString , displayName)]

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
otherAgents = [agentRando, agentRando]

# Create a new game for each agent we are comparing agaisnt
envs = []
for agent in otherAgents:
    env = rlcard.make('limit-holdem')
    env.set_agents([mainAgent, agent])
    envs.append(env)
scores = [[] for _ in range(0,len(otherAgents))]

# Create placeholder for our plot that will be generated below
root = tk.Tk()
fig, ax = plt.subplots()
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(column=0,row=1)

# Runs when graph is initially shown
def init():
    return ax,

# Runs every iteration. i Is the iteration count
def update(i):
    ax.clear()
    for gameNum, env in enumerate(envs):
        newResults = tournament(env, 50)
        scores[gameNum].append(newResults)
        ax.plot(range(0,len(scores[gameNum])), [s[1] for s in scores[gameNum]])
    ax.plot(range(0,len(scores[0])), [0 for _ in scores[0]])

    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)
    plt.title('Player Tester')
    plt.ylabel('Earnings after 50 hands')
    return ax,

# Puts updating the graph on a loop
ani = FuncAnimation(fig, update, frames=range(0,10000), init_func=init, blit=True)  
root.mainloop()