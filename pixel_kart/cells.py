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
        """
        Retrieve the Color object associated with the current Cell flag.

        Note:
            If multiple flags are combined within a single Cell instance, 
            the behavior depends on the mapping keys in `CELL_TO_COLOR`.

        Returns:
            Color: The color scheme matching the cell type.
        """
        return CELL_TO_COLOR[self]

CELL_TO_COLOR = {
    Cell.WALL: Color.BLACK,
    Cell.GRASS: Color.GREEN,
    Cell.ROAD: Color.GREY,
    Cell.START_LINE: Color.SPECIAL,     # Text is normally white so SPECIAL is white too by default. (special cells)
    Cell.FINISH_LINE: Color.SPECIAL,    # This also avoids players to choose white color
    Cell.CHECKPOINT: Color.SPECIAL      # to represent themselves so it works well!
}
"""
dict[Cell, Color]: Map each discrete cell flag to its corresponding rendering color.
"""

def cell_to_labels(cell: Cell) -> str:
    """
    Convert a cell's flags into a string representation composed of graphical emojis.

    Note:
        Cells can contain combined bitwise flags (e.g., a combination of terrain and 
        special markers). If multiple flags containing active labels are present within 
        the cell, their labels are concatenated. If the resulting string contains more 
        than one label character, it is enclosed in square brackets.

    Args:
        cell (Cell): The cell instance (or bitwise combination of flags) to evaluate.

    Returns:
        str: A string of concatenated emojis matching the active flags, 
             wrapped in brackets if multiple labels match.
    """
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
dict[Cell, str]: Map each cell flag to its descriptive emoji label used for GUI rendering.
"""

LEGACY_LABEL_TO_CELL = {
    'W': Cell.WALL,
    'G': Cell.GRASS,
    'R': Cell.ROAD,
    'F': Cell.START_LINE
}
"""
dict[str, Cell]: Parser map for legacy text-based track configurations. 
                 Maps historical single-character representations to modern Cell flags.
                 Note that 'F' maps to START_LINE as older formats used a unified line asset.
"""

TERRAIN_BITMASK = Cell.WALL | Cell.GRASS | Cell.ROAD
"""
Cell: Bitmask encompassing all environment terrain flags (WALL, GRASS, ROAD).
"""

SPECIAL_BITMASK = Cell.START_LINE | Cell.FINISH_LINE | Cell.CHECKPOINT
"""
Cell: Bitmask encompassing all game logic trigger flags (START_LINE, FINISH_LINE, CHECKPOINT).
"""
