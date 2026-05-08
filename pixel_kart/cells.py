from pixel_kart.colors import Color
from enum import IntFlag

class Cell(IntFlag):
    """
    Enumeration representing the state of a board cell.

    Uses integer flags for efficient storage and comparison.
    There is a start line, a finish line, and a checkpoint that should
    be placed either next to the finish line (the direction from which the player must cross),
    or next to the start line (the direction the player must follow).

    Just don't place the checkpoint on the shortest path between the lines...
    otherwise there's no point in making a huge road and not follow it.
    """
    WALL = 1
    GRASS = 2
    ROAD = 4
    START_LINE = 8
    FINISH_LINE = 16
    CHECKPOINT = 32

    @property
    def color(self) -> Color:
        return CELL_TO_COLOR[self]

CELL_TO_COLOR = {
    Cell.WALL: Color.BLACK,
    Cell.GRASS: Color.GREEN,
    Cell.ROAD: Color.GREY,
    Cell.START_LINE: Color.SPECIAL,     # Text is normally white so SPECIAL is white too. (special cells)
    Cell.FINISH_LINE: Color.SPECIAL,    # This also avoids players to choose white color
    Cell.CHECKPOINT: Color.SPECIAL      # to represent themselves!
}
"""
Map each cell to its color.
"""

def cell_to_labels(cell: Cell) -> str:
    labels = ''.join([
        label
        for c, label in CELL_TO_LABEL.items()
        if c in cell
    ])
    if len(labels) > 1:
        labels = f"[{labels}]"
    return labels

CELL_TO_LABEL = {
    Cell.WALL: '',
    Cell.GRASS: '',
    Cell.ROAD: '',
    Cell.START_LINE: '🏁',
    Cell.FINISH_LINE: '🚩',
    Cell.CHECKPOINT: '⭐'
}
"""
Map each cell to its label.  
Used in the GUI.
"""

LEGACY_LABEL_TO_CELL = {
    'W': Cell.WALL,
    'G': Cell.GRASS,
    'R': Cell.ROAD,
    'F': Cell.START_LINE
}
"""
For legacy text import.
"""

TERRAIN_BITMASK = Cell.WALL | Cell.GRASS | Cell.ROAD
SPECIAL_BITMASK = Cell.START_LINE | Cell.FINISH_LINE | Cell.CHECKPOINT
"""
Bitmasks to help separate terrain from specials.
"""
