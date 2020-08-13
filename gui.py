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
selectedAgent = ""
selectedAgentName = ""
envName = ""
selectedAgainstAgents = []
selectedAgainstAgentNames = []

def get_all_games():
    ''' Finds all registered games

    returns:
        games (string): name of gamees available
    '''
    return list(EnvReg.registry.env_specs.keys())

def get_all_trained_agents(gameName=None):
    ''' Checks for all registered pre-trained agents

    args:
        gameName (string): optional. Will only return agents trained
            for the game specified. Has to be an exact match.

    returns:
        Agents (list of object): list of agent objects
        Agent Names (List of string): agent's name
    '''
    allAgents = []
    agentNames = []
    for agent in ModelReg.model_registry.model_specs.values():
        if gameName == None or agent.game == gameName:
            agentNames.append(agent.model_id)
            allAgents.append(agent.load().agents[0]) # assumes player is P1
    return (allAgents, agentNames)

def make_game(players, gameName):
    ''' Creates an enviorment for tournament play.

    args:
        players (list of agents): Agent's to play
        gameName (string): name of the game to play

    returns:
        env (Env): Game that is ready to play
    '''
    env = rlcard.make(gameName)
    env.set_agents(players)
    return env

def set_game_name(selectedTuple):
    ''' Called when user selects a game to play.  Also, Updates display string.

    args:
        selectedTuple (int): index into the game options list
    '''    
    global envName
    gameIndex = int(selectedTuple[0])
    envName = games[gameIndex]
    update_status_string()

def set_agent_name(selectedTuple):
    ''' Called when user selects a main agent.  Also, Updates display string.

    args:
        selectedTuple (int): index into the agent options list
    '''   
    global selectedAgent, selectedAgentName
    agentIndex = int(selectedTuple[0])
    selectedAgent = allAgents[agentIndex]
    selectedAgentName = agentNames[agentIndex]
    update_status_string()

def set_against_agent_name(selectedTuple):
    ''' Called when user selects an agent to play against.  Also, Updates display string.

    args:
        selectedTuple (int): index into the agent options list
    '''   
    global selectedAgainstAgents, selectedAgainstAgentNames
    agentIndex = int(selectedTuple[0])
    selectedAgainstAgents.append(allAgents[agentIndex])
    selectedAgainstAgentNames.append(agentNames[agentIndex])
    update_status_string()
    
def clear_against_agents():
    ''' Called when user clears selected agents.  Also, Updates display string.
    '''  
    global selectedAgainstAgents, selectedAgainstAgentNames
    selectedAgainstAgents = []
    selectedAgainstAgentNames = []
    update_status_string()

def update_status_string():
    ''' Called when user clears selected agents.  Also, Updates display string.
    '''  
    global statusString, selectedAgentName, selectedAgainstAgentNames, envName
    statusString.set("Game:\n" + envName + "\nMain Agent:\n" + selectedAgentName +
        "\nAgainst Agents:\n" + "\n".join(selectedAgainstAgentNames))

def startGame():
    ''' Called when user clicks start game.  Kicks off chart animations.
    '''  
    global scores, acumScores, envs, gamesPlayed, fig, fig2, ax, ax2
    envs = []
    for agent in selectedAgainstAgents:
        envs.append(make_game([selectedAgent, agent], envName))
    scores = [[] for _ in enumerate(selectedAgainstAgents)]
    acumScores = [0 for _ in enumerate(selectedAgainstAgents)]
    gamesPlayed = [[] for _ in enumerate(selectedAgainstAgents)]

    fig = plt.figure()
    ax = plt.axes()
    # ax.set_ylim(-1,1)
    fig.suptitle("Rewards Per Game")
    fig2 = plt.figure()
    ax2 = plt.axes()
    # ax2.autoscale()
    fig2.suptitle("Accumulative Rewards")

    FuncAnimation(fig, update, init_func=init, blit=True, frames=200, interval=20)
    FuncAnimation(fig2, update2, init_func=init2, blit=True, frames=200, interval=20)
    plt.show()

def saveRun():
    ''' Called when user clicks the save button.  Dumps all of the raw game data in
        a JSON format.
    '''  
    global gamesPlayed
    saveTypes = [("JSON Files", "*.json")]
    toSave = asksaveasfile(filetypes = saveTypes, defaultextension = saveTypes)
    toSave.write(str(gamesPlayed))
    toSave.close()

def init():
    ''' Required for FuncAnimation.  Just returns the original axes

        returns:
            axes (Axes): the original axes
    '''  
    return ax,

def update(i):
    ''' Generates the next game of data, and updates the per game graph

        args:
            i (int): current iteration number
        returns:
            axes (Axes): the original axes
    '''  
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

def init2():
    ''' Required for FuncAnimation.  Just returns the original axes

        returns:
            axes (Axes): the original axes
    '''  
    return ax2,

def update2(i):
    ''' Generates the next game of data, and updates the acumulative graph.

        args:
            i (int): current iteration number
        returns:
            axes (Axes): the original axes
    '''  
    global acumScores
    ax2.clear()
    ax2.bar(selectedAgainstAgentNames, acumScores, label=selectedAgainstAgentNames)
    ax2.grid('on')
    ax2.legend(labels=selectedAgainstAgentNames)
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
tk.Button(root, text="Pick A Game", command= lambda: set_game_name(gameListBox.curselection())).grid(column=0,row=2)

# List the agent options
agentListBox = tk.Listbox(root, width=40, yscrollcommand=1)
for item in agentNames:
    agentListBox.insert(tk.END, item)

agentListBox.grid(column=1,row=1)
tk.Button(root, text="Pick Main Agent", command= lambda: set_agent_name(agentListBox.curselection())).grid(column=1,row=2)
tk.Button(root, text="Add Against Agent", command= lambda: set_against_agent_name(agentListBox.curselection())).grid(column=1,row=3)
tk.Button(root, text="Clear Against Agents", command= lambda: clear_against_agents()).grid(column=1,row=4)

# Display the information about the current game
statusString = tk.StringVar()
statusLabel = tk.Label(root, textvariable=statusString)
statusLabel.grid(column=2,row=1)
update_status_string()

tk.Button(root, text="Start Game", command=startGame).grid(column=2,row=2)
tk.Button(root, text="Save Run", command=saveRun).grid(column=2,row=3)

root.mainloop()