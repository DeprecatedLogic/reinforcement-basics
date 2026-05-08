from random import choice, randint
import pickle
from pixel_kart.player import Player
from pixel_kart.actions import Action
from pixel_kart.cells import Cell, CELL_TO_LABEL, cell_to_labels
import logging
logger = logging.getLogger(__name__)

class Board:
    """
    Represents the game board grid.
    """
    
    def __init__(self, rows: int, columns: int) -> None:
        """
        Initialize the board with given dimensions.

        Args:
            rows (int): Number of rows.
            columns (int): Number of columns.
        """
        self.grid: list[list[Cell]] = []
        self.rows = rows
        self.columns = columns
        self.start_line: set[tuple[int, int]] = set()
        self.finish_line: set[tuple[int, int]] = set()
    
    @staticmethod
    def load(grid: list) -> Board:
        """
        Create a Board instance from a 2D list (grid).
    
        Args:
            grid (list): 2D list containing Cells.
    
        Returns:
            Board: A Board instance initialized with the loaded data.
        """
        logger.debug(f"Initializing Board out of a 2D list")
        rows = len(grid)
        columns = len(grid[0])
        board = Board(rows, columns)
        for row in range(rows):
            for column in range(columns):
                board[row, column] = grid[row][column]
        
        # We did not check for invalid cells or other errors
        # so it might cause problems later in-game
        return board

    @property
    def rows(self) -> int:
        """
        Get the number of rows in the board.

        Returns:
            int: Number of rows
        """
        return self._rows if hasattr(self, '_rows') else 0
    
    @rows.setter
    def rows(self, value: int) -> None:
        if value < 1:
            logger.error(f"Invalid rows value: {value}")
            raise ValueError("Rows value must be bigger than 0!")

        current = self.rows
        if value == current:
            return

        # Add rows
        if len(self.grid) < value:
            for _ in range(value - len(self.grid)):
                self.grid.append([[] for _ in range(self.columns)])

        # Remove extra rows
        elif len(self.grid) > value:
            del self.grid[value:]

        # Normalize all rows to correct column count
        for row in self.grid:
            if len(row) < self.columns:
                row.extend([[] for _ in range(self.columns - len(row))])
            elif len(row) > self.columns:
                del row[self.columns:]

        self._rows = value
        
    @property
    def columns(self) -> int:
        """
        Get the number of columns in the board.
        
        Returns:
            int: Number of columns.
        """
        return self._columns if hasattr(self, '_columns') else 0
    
    @columns.setter
    def columns(self, value: int) -> None:
        if value < 1:
            logger.error(f"Invalid columns value: {value}")
            raise ValueError("Columns value must be bigger than 0!")

        current = self.columns
        if value == current:
            return

        for row in self.grid:
            # Add columns
            if len(row) < value:
                row.extend([[] for _ in range(value - len(row))])

            # Remove extra columns
            elif len(row) > value:
                del row[value:]

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

    def __str__(self) -> str:
        """
        Return a string representation of the board for saving purposes.

        Returns:
            str: An ASCII version of the board's grid.
        """
        result = []
        
        for row in self.grid:
            temp = []
            
            for cell in row:
                temp.append(cell_to_labels(cell))

            result.append(''.join(temp))

        return '\n'.join(result)

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

        if value & Cell.START_LINE:
            self.start_line.add(position)
            logger.debug(f"START_LINE cell detected, storing the position {position}")
        if value & Cell.FINISH_LINE:
            self.finish_line.add(position)
            logger.debug(f"FINISH_LINE cell detected, storing the position {position}")
            
        logger.debug(f"Cell {position} set to {value.name}")

class GameModel:
    """
    Represents the overall game state.

    Tracks the board, players, current turn, and history of actions.
    """

    def __init__(self, board: Board, *players: Player, laps_required: int = 1) -> None:
        """
        Initialize the game model with a board and players.

        Args:
            board (Board): The game board.
            players (tuple[Player]): Players participating in the game.
            laps_required (int): The number of laps a player needs to complete.
        """
        logger.info(f"Initializing game with {len(players)} players")

        self.board = board
        self.players = players
        self.laps_required = laps_required if laps_required > 0 else 1
        self.laps_completed: dict[Player, int] = {}
        self.actions_history: dict[Player, Action] = {}
        self.game_turns = 0
        
        # Storing current player index
        self.current_player_index = 0
        
        # Initialize the model's data
        logger.info("Initializing the game model using the reset method")
        self.reset()

    def _assign_initial_turn(self) -> None:
        """
        Randomly select which player starts the game.
        """
        self.current_player_index = randint(0, len(self.players)-1)
        logger.debug(f"Initial player index: {self.current_player_index}")

    def _assign_initial_positions(self) -> None:
        """
        Assign starting positions to all players.

        Players are placed on the start line.
        Raises an exception if there are more players than available positions.
        """
        available_positions = list(self.board.start_line)

        for player in self.players:
            if available_positions:
                position = choice(available_positions)
                available_positions.remove(position)
                
                player.position = position
                logger.debug(f"{player.name} assigned to {position}")
            else:
                logger.critical("More players than available starting positions")
                raise Exception(
                    "Too many players for available starting positions"
                )

    def assign_position(self, player: Player, position: tuple[int, int]) -> Cell:
        """
        Move a player to a new position on the board and record the action.

        Args:
            player (Player): The player to move.
            position (tuple[int, int]): Target (row, column) coordinates.

        Returns:
            Cell: The board cell at player's position.
        """
        logger.debug(f"{player.name} moving to {position}")

        self.actions_history[player].append(player.position)
        player.position = position

        return self.board[position]

    def current_player(self) -> Player:
        """
        Get the current active player.

        Returns:
            Player: The player whose turn it is.
        """
        return self.players[self.current_player_index]

    def update_turn(self) -> None:
        self.game_turns += 1
        for player in self.players:
            if not player.crashed:
                player.nb_turns = self.game_turns

    def reset(self) -> None:
        """
        Reset the game model to its initial state.

        Resets the board, clears action history, reassigns positions,
        and selects the starting player randomly.
        """
        logger.info("Resetting game model")
        self.game_turns = 0
        
        # Store laps completed (0) for each player and reset them
        for player in self.players:
            player.reset_kart()
            self.laps_completed[player] = 0
            # In case we might need it in the future for replays, etc.
            self.actions_history[player] = []
            
        self._assign_initial_positions()
        self._assign_initial_turn()

    def get_opponents(self) -> tuple[Player]:
        """
        Get a tuple containing all players except the current player.

        Returns:
            tuple[Player]: Opponents of the current player.
        """
        return tuple(player for player in self.players if player != self.current_player())
    