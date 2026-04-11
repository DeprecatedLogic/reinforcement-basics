from enum import Enum

class Action(Enum):
    """
    Enumeration of all possible movement actions.

    Each action represents a direction and is associated with a (row, column) delta.
    """

    UP = (-1, 0)
    RIGHT = (0, 1)
    DOWN = (1, 0)
    LEFT = (0, -1)

    @property
    def delta(self) -> tuple[int, int]:
        """
        Return the movement delta associated with the action.

        Returns:
            tuple[int, int]: (delta_row, delta_column)
        """
        return self.value


ACTION_DELTAS = {action.value for action in Action}
"""
Set of all valid movement deltas.  
Used for fast validation of allowed moves.
"""

KEY_TO_ACTION = {
    "w": Action.UP,
    "s": Action.DOWN,
    "a": Action.LEFT,
    "d": Action.RIGHT,
    "up": Action.UP,
    "down": Action.DOWN,
    "left": Action.LEFT,
    "right": Action.RIGHT
}
"""
Mapping of keyboard inputs to actions.  
Supports both WASD keys and arrow keys for movement.
"""

ACTION_TO_INDEX = {
    Action.UP: 0,
    Action.DOWN: 1,
    Action.LEFT: 2,
    Action.RIGHT: 3
}
"""
Mapping of actions to their respective index.  
This avoids repeatedly deriving indices (via iteration or lookup on the Action enum),
providing constant-time access.
"""
