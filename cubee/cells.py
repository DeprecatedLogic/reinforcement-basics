from enum import IntEnum

class Cell(IntEnum):
    """
    Enumeration representing the state of a board cell.

    Each value corresponds to either an empty cell or ownership by a player.
    Uses integers for efficient storage and comparison.
    """
    EMPTY = 0
    P1 = 1
    P2 = 2
    P3 = 3
    P4 = 4
