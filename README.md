# Reinforcement Learning Basics

A collection of three simple games designed to demonstrate Reinforcement Learning (RL) principles using Python and Tkinter. The project features agents that learn to play and win autonomously through trial and error.

## The Games
### Matches (Nim)
A classic logic game played by two players.  
Players take turns removing 1, 2, or 3 matches. The player forced to take the last match loses.

### Cubee
A strategic territory game played on a 5x5 grid.  
Players move across tiles to claim them. You cannot move onto an opponent's tile or out of bounds. The game ends when no free tiles remain.

### PixelKart
A simplified racing simulation.  
The player (a pixel) must navigate through a circuit as fast as possible.

## Learning Mechanics
The core of this project is the learning AI. Unlike the simplified AI (pre-defined actions) also included in the games, the learning agent improves over time.  
The agent tries random moves to discover the game rules, receives psotive feedback for winning (or even fast times) and negative feedback for losing (or wrong moves) which then help the agent update its internal **Q-table** or **value function** after every game to *reinforce* successful strategies.

## Prerequisites
- Make sure you have git installed.
- Make sure you have Python version 3.11 or newer installed.  
  For Windows, you can find the official download page for Python [here](https://www.python.org/downloads/).  
**Note:** If you want to avoid using git, you can also download the repository as a *zip* file and skip step 2 in the [Getting Started](#getting-started) section.

## Getting Started

1. Clone the repository and navigate to the directory
```sh
git clone https://github.com/ItzKarizma/reinforcement-basics.git
cd reinforcement-basics
```

2. Create and configure a virtual environment for Python
```sh
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
```
**Note:** On Linux use the command `source venv/bin/activate`.

3. Install dependencies
```sh
pip install -r requirements.txt
```

4. Launch the program
```sh
python main.py
```

## Author Notes
*My AI learns from its mistakes; I just drink coffee and hope the code works.* - [ItzKarizma](https://github.com/ItzKarizma)  
*Watched an AI learn faster than me. I’m fine. Totally fine.* - [EgoChaxs](https://github.com/EgoChaxs)

## License
Licensed under the MIT license. See the LICENSE file for details.