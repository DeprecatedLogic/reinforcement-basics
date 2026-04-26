from enum import Enum

class Direction(Enum):
    """
    Enumeration of all possible directions.

    Each direction is associated with a (row, column) delta.
    """

    NORTH = (-1, 0)
    EAST = (0, 1)
    SOUTH = (1, 0)
    WEST = (0, -1)

    @property
    def delta(self) -> tuple[int, int]:
        """
        Return the movement delta associated with the direction.

        Returns:
            tuple[int, int]: (delta_row, delta_column)
        """
        return self.value

DIRECTION_DELTAS = (direction.value for direction in Direction)
"""
A tuple containing all direction deltas.
"""

DIRECTION_ORDER = (Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST)
"""
Required for left/right turns or reverse.
Each player needs to keep track of the direction they're facing by holding
an index and increasing/decreasing it based on the turn (left/right) they take.
"""