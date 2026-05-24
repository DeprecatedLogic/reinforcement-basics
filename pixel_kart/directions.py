from enum import Enum

class Direction(Enum):
    """
    Enumeration of all possible absolute directions on the game grid.

    Each direction maps to a coordinate delta vector on a 2D matrix layout, 
    where row indices increase downwards and column indices increase to the right.

    Attributes are defined in a clockwise rotational order (important for rotations).
    """

    NORTH = (-1, 0)
    EAST = (0, 1)
    SOUTH = (1, 0)
    WEST = (0, -1)

    @property
    def delta(self) -> tuple[int, int]:
        """
        Retrieve the movement delta vector associated with the current direction.

        Returns:
            tuple[int, int]: A tuple of integers representing `(delta_row, delta_column)`.
        """
        return self.value

DIRECTION_DELTAS = tuple(direction.value for direction in Direction)
"""
tuple: A tuple containing coordinate delta tuples for each direction.

Note:
    We might remove this because we basically used `DIRECTION_ORDER[index].delta` every time,
    or we might change the code in a future update and use `DIRECTION_DELTAS[index]` instead.
"""

DIRECTION_ORDER = (Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST)
"""
tuple[Direction, ...]: A sequence defining the clockwise rotational order of directions.

Note:
    This order is crucial for executing situational maneuvers such as left/right turning 
    and reversing. Karts maintain their orientation by holding an integer index pointing 
    to this tuple, wrapping around the boundaries using modulo arithmetic when changing direction.
"""