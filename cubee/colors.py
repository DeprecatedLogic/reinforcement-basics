from enum import Enum

class Color(Enum):
    """
    Enumeration of possible colors used in the game.

    Includes a special `EMPTY` color for unclaimed cells.
    Values are strings representing the color names.
    """
    BG = "#2C3E50"
    FG = "#FFFFFF"
    EMPTY = "white"
    WHITE = "white"
    BLACK = "black"
    ORANGE = "orange"
    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    YELLOW = "yellow"
    PINK = "pink"
    PURPLE = "purple"
