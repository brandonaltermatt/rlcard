import tkinter as tk
from pandas import DataFrame
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

env = rlcard.make('limit-holdem', config={'seed': 0, "game_player_num": 4})
set_global_seed(0)

# Set up agents
agentRando = RandomAgent(action_num=env.action_num)
agentOneLook = OneLookAgent(action_num=env.action_num)
env.set_agents([agentRando, agentOneLook])

# Test
agentNames = ["Random1", "One Look"]
root = tk.Tk()
fig, ax = plt.subplots()

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(column=0,row=1)
scores = []

def init():
    return ax,

def update(i):
    newResults = tournament(env, 50)
    scores.append(newResults)
    # runningAverage = [0 for _ in range(0,len(xAxis))]
    # for score in scores:
    #     for i, agentScore in enumerate(score):
    #         runningAverage[i] += agentScore
    #print(runningAverage)
    ax.clear()
    for i in range(0,len(scores[0])):
        ax.plot(range(0,len(scores)), [s[i] for s in scores])
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)
    plt.title('TMP102 Temperature over Time')
    plt.ylabel('Temperature (deg C)')
    return ax,

ani = FuncAnimation(fig, update, frames=range(0,10000), init_func=init, blit=True)  
root.mainloop()