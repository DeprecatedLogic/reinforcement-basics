from random import choice, randint
from cubee.player import Player
from cubee.actions import ACTION_DELTAS
from cubee.cells import Cell
import logging
logger = logging.getLogger(__name__)

class Board:
    """
    Represents the game board grid.

    Handles storage of cells, provides access to neighbors, counts cell types, 
    and tracks modifications caused by enclosures.
    """
    
    def __init__(self, rows: int, columns: int) -> None:
        """
        Initialize the board with given dimensions.

        Args:
            rows (int): Number of rows.
            columns (int): Number of columns.
        """
        self.rows = rows
        self.columns = columns
        self.grid = [[Cell.EMPTY for _ in range(columns)] for _ in range(rows)]
        
        # Modified cells after enclosure
        self.enclosure_modified_cells: list[tuple[int, int]] = []

    @property
    def rows(self) -> int:
        """
        Get the number of rows in the board.

        Returns:
            int: Number of rows
        """
        return self._rows
    
    @rows.setter
    def rows(self, value: int) -> None:
        """
        Set the number of rows.

        Args:
            value (int): New row count.

        Raises:
            ValueError: If value < 1.
        """
        if value < 1:
            logger.error(f"Invalid rows value: {value}")
            raise ValueError("Rows value must be bigger than 0!")
        self._rows = value
        
    @property
    def columns(self) -> int:
        """
        Get the number of columns in the board.
        
        Returns:
            int: Number of columns.
        """
        return self._columns
    
    @columns.setter
    def columns(self, value: int) -> None:
        """
        Set the number of columns.

        Args:
            value (int): New column count.

        Raises:
            ValueError: If value < 1.
        """
        if value < 1:
            logger.error(f"Invalid columns value: {value}")
            raise ValueError("Columns value must be bigger than 0!")
        self._columns = value

    @property
    def size(self) -> tuple[int, int]:
        """
        Return the board size as a tuple (rows, columns).

        Returns:
            tuple[int, int]: (rows, columns)
        """
        return self.rows, self.columns

    @size.setter
    def size(self, value: tuple[int, int]) -> None:
        """
        Set the board size.

        Args:
            value (tuple[int, int]): New size as (rows, columns).
        """
        self.rows, self.columns = value

    def is_within_bounds(self, row: int, column: int) -> bool:
        """
        Check if a position is within the board boundaries.

        Args:
            row (int): Row index.
            column (int): Column index.

        Returns:
            bool: True if the position is within bounds.
        """
        return 0 <= row < self.rows and 0 <= column < self.columns

    def get_neighbors(self, row: int, column: int) -> list[tuple[int, int]]:
        """
        Get all valid neighboring positions for a given cell.

        Args:
            row (int): Row index.
            column (int): Column index.

        Returns:
            list[tuple[int, int]]: List of neighboring (row, column) positions.
        """
        neighbors = []

        for delta in ACTION_DELTAS:
            delta_row, delta_column = delta
            neighbor_row = row + delta_row
            neighbor_column = column + delta_column

            if self.is_within_bounds(neighbor_row, neighbor_column):
                neighbors.append((neighbor_row, neighbor_column))
                
        return neighbors

    def count_cells(self) -> dict[Cell, int]:
        """
        Count the number of cells of each type on the board.

        Returns:
            dict[Cell, int]: Mapping of cell type to count.
        """
        cells_counter = {cell: 0 for cell in Cell}
        for row in self.grid:
            for cell in row:
                cells_counter[cell] += 1
        return cells_counter
    
    def reset(self) -> None:
        """
        Reset the board to all EMPTY cells and clear modified cells.
        """
        for row in self.grid:
            row[:] = [Cell.EMPTY] * len(row)
        self.enclosure_modified_cells.clear()
        
        logger.debug("Board reset")

    def __str__(self) -> str:
        """
        Return a string representation of the board for printing.
        Adapts to multi-digit cell values and ensures horizontal lines reach the last column.

        Returns:
            str: An ASCII version of the board's grid.
        """
        # Determine the width of a single column
        max_cell_value_length = max(len(str(cell.value)) for row in self.grid for cell in row)

        # Build the horizontal line
        number_of_columns = len(self.grid[0])
        line_str = "-" * ((max_cell_value_length + 3) * number_of_columns + 1) + "\n"

        # Build the grid string
        grid_str = line_str
        for row in self.grid:
            row_cells = [f"{str(cell.value).rjust(max_cell_value_length)}" for cell in row]
            row_str = " | ".join(row_cells)
            grid_str += f"| {row_str} |\n"
            grid_str += line_str

        return grid_str.strip()

    def __getitem__(self, position: tuple[int, int]) -> Cell:
        """
        Get the cell value at a specific position.

        Args:
            position (tuple[int, int]): (row, column) coordinates.

        Returns:
            Cell: The cell at the given position.
        """
        row, column = position
        return self.grid[row][column]

    def __setitem__(self, position: tuple[int, int], value: Cell) -> None:
        """
        Set the cell value at a specific position.

        Args:
            position (tuple[int, int]): (row, column) coordinates.
            value (Cell): The cell type to set.
        """
        row, column = position
        self.grid[row][column] = value
        logger.debug(f"Cell {position} set to {value.name}")

class GameModel:
    """
    Represents the overall game state.

    Tracks the board, players, current turn, and history of actions.
    """

    def __init__(self, board: Board, *players: list[Player]) -> None:
        """
        Initialize the game model with a board and players.

        Args:
            board (Board): The game board.
            players (list[Player]): Players participating in the game.
        """
        logger.info(f"Initializing game with {len(players)} players")

        self.board = board
        self.players = players

        # Storing current player index
        self.current_player_index = 0
        
        # Mapping between Cell and Player
        self.cell_to_player = {}

        self._assign_cell_identities()
        self._assign_initial_positions()
        self._assign_initial_turn()
        
        # In case we might need it in the future for replays, etc.
        self.actions_history: dict[Cell, list[tuple[int, int]]] = {player.cell: [] for player in players}

    def _assign_initial_turn(self) -> None:
        """
        Randomly select which player starts the game.
        """
        self.current_player_index = randint(0, len(self.players)-1)
        logger.debug(f"Initial player index: {self.current_player_index}")

    def _assign_initial_positions(self) -> None:
        """
        Assign starting positions to all players.

        Players are placed in board corners.
        Raises an exception if there are more players than available positions.
        """
        corner_positions = [
            (0, 0),
            (0, self.board.columns-1),
            (self.board.rows-1, 0),
            (self.board.rows-1, self.board.columns-1)
        ]
        for player in self.players:
            if corner_positions:
                corner = choice(corner_positions)
                corner_positions.remove(corner)
                
                player.position = corner
                self.board[player.position] = player.cell
                logger.debug(f"{player.name} assigned to {corner}")
            else:
                logger.critical("More players than available starting positions")
                raise Exception(
                    "Too many players for available starting positions"
                )

    def _assign_cell_identities(self) -> None:
        """
        Assign a unique Cell identity to each player.

        Raises:
            Exception: If there are more players than available cell identities.
        """
        cells = list(Cell)[1:]
        if len(cells) < len(self.players):
            logger.critical("More players than available cell identities")
            raise Exception("Too many players for available cell identities")

        for i in range(len(self.players)):
            self.players[i].cell = cells[i]
            self.cell_to_player[cells[i]] = self.players[i]
            logger.debug(f"{self.players[i].name} assigned cell {cells[i].name}")

    def assign_position(self, player: Player, position: tuple[int, int]) -> None:
        """
        Move a player to a new position on the board and record the action.

        Args:
            player (Player): The player to move.
            position (tuple[int, int]): Target (row, column) coordinates.
        """
        logger.debug(f"{player.name} moving to {position}")

        self.board[position] = player.cell
        self.actions_history.setdefault(player.cell, [])
        self.actions_history[player.cell].append(player.position)
        player.position = position

    def current_player(self) -> Player:
        """
        Get the current active player.

        Returns:
            Player: The player whose turn it is.
        """
        return self.players[self.current_player_index]

    def reset(self) -> None:
        """
        Reset the game model to its initial state.

        Resets the board, clears action history, reassigns positions, 
        and randomly selects the starting player.
        """
        logger.info("Resetting game model")

        self.board.reset()
        self.actions_history.clear()
        self._assign_initial_positions()
        self._assign_initial_turn()

    def get_opponents(self) -> list[Player]:
        """
        Get a list of all players except the current player.

        Returns:
            list[Player]: Opponents of the current player.
        """
        return [player for player in self.players if player != self.current_player()]
    