from enum import Enum, auto

class Action(Enum):
    """
    Enumeration of all possible actions.
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
Mapping of keyboard inputs to actions.  
Supports both WASD keys and arrow keys for movement (using spacebar for Action.NOTHING).
"""

AVAILABLE_ACTIONS = (
    Action.ACCELERATE, Action.BRAKE,
    Action.TURN_LEFT, Action.TURN_RIGHT, Action.NOTHING
)
"""
A tuple containing all actions.
"""
