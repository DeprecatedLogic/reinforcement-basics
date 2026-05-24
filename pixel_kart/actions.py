from enum import Enum, auto

class Action(Enum):
    """
    Enumeration of all possible mechanical and structural actions in the game.
    """

    ACCELERATE = auto()
    BRAKE = auto()
    TURN_LEFT = auto()
    TURN_RIGHT = auto()
    NOTHING = auto()
    CHEAT = auto() # testing purposes

KEY_TO_ACTION = {
    "w": Action.ACCELERATE,
    "up": Action.ACCELERATE,

    "s": Action.BRAKE,
    "down": Action.BRAKE,
    
    "a": Action.TURN_LEFT,
    "left": Action.TURN_LEFT,

    "d": Action.TURN_RIGHT,
    "right": Action.TURN_RIGHT,

    "space": Action.NOTHING,
    "return": Action.NOTHING,

    # test cheating (for fun)
    "shift_l": Action.CHEAT
}
"""
dict[str, Action]: Mapping of keyboard inputs to actions.  
Supports both WASD keys and arrow keys for movement (using spacebar or return for Action.NOTHING).  
The string keys correspond directly to Tkinter key symbols (`event.keysym`).
"""

AVAILABLE_ACTIONS = (
    Action.ACCELERATE, Action.BRAKE,
    Action.TURN_LEFT, Action.TURN_RIGHT, Action.NOTHING
)
"""
tuple[Action, ...]: The standard action space available to all regular players 
    (both humans and Reinforcement Learning agents) during normal gameplay. 
    Excludes testing hooks like Action.CHEAT.
"""
