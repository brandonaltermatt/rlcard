### A graphical user interface was created to allow for users to test compare the performance of different agents
# User Guide
## Launching
```
python gui.py
```
## Selecting Game
* Select a game in the far left list
* Click the "Pick A Game" Button
* The game should be populated on the right side of UI
<img width="500" src="./docs/imgs/GUI_select_game.png" alt="Select Game" />

## Setting Main Agent
The main agent is the agent that will be facing 1 to many other agents.  This will most likely be the agent you
have developed.
* Select an agent from the list on the right
* Click the "Pick Main Agent" Button
* The agent should be populated on the right side of UI
<img width="500" src="./docs/imgs/GUI_select_main_agent.png" alt="Main Agent" />

## Setting Other Agents
The other agent(s) selected are the agent's your "Main Agent" will be facing.  When multiple other agent's are
selcted, the main agent will play a game agaisnt each agent selected.
* Select an agent from the list on the right
* Click the "Add Against Agent" Button
* The agent should be populated on the right side of UI
This process should be repeated for each agent you would like to play against.  In the example below, two
opponents are selected.
<img width="500" src="./docs/imgs/GUI_select_other_agents.png" alt="Other Agents" />

## Removing Opponents
To reset the opponent's list, click the "Clear Agaisnt Agents"
<img width="500" src="./docs/imgs/GUI_select_other_agents.png" alt="Clear Agents" />

## Starting Game Play
Now that all of the agents are ready, click the "Start Game" button.  Two Graphs will be generated.  The graphs
represent the relative rewards of the agaisnt agents.  The main agent will always be shown as 0, because the agent
can be playing agaisnt multiple opponents. This mean's other agent's having negative rewards indicates the main
agent is winning.
<img width="500" src="./docs/imgs/GUI_graph.png" alt="Other Agents" />

# Developer Guide
Code for the GUI is self contained with the exception of the items below.
## Adding new Games
Games are registered in rlcard/envs/init.py .  There is a series of register function calls.  AN exmaple is below
```
register(
    env_id='short-limit-holdem',
    entry_point='rlcard.envs.shortlimitholdem:ShortlimitholdemEnv',
)
```
In this example, the game will be refereed to as 'short-limit-holdem' in the GUI.
## Adding new Agents
Trained agents are registered in rlcard/models/init.py .  There is a series of register function calls.  An exmaple is below
```
register(
    model_id='short-limit-holdem-one-look',
    entry_point='rlcard.models.one_look_models:OneLookModelShortHoldem')
```
In this example, the game will be refereed to as 'short-limit-holdem-one-look' in the GUI.
