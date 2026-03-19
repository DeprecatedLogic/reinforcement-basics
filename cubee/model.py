from random import choice, randint
from cubee.player import Player
from cubee.actions import ACTION_DELTAS
from cubee.cells import Cell

class Board:
    """
    Represents the game grid and manages all board-related logic.
    Stores cell ownership, provides neighbor access.
    """
    
    def __init__(self, rows: int, columns: int) -> None:
        """_summary_

        Args:
            rows (int): _description_
            columns (int): _description_
        """
        self.rows = rows
        self.columns = columns
        self.grid = [[Cell.EMPTY for _ in range(columns)] for _ in range(rows)]
        
        # Modified cells after enclosure
        self.enclosure_modified_cells: list[tuple[int, int]] = []

    @property
    def rows(self) -> int:
        """_summary_

        Returns:
            int: _description_
        """
        return self._rows
    
    @rows.setter
    def rows(self, value: int) -> None:
        """_summary_

        Args:
            value (int): _description_

        Raises:
            Exception: _description_
        """
        if value < 1:
            raise ValueError("Rows value should be bigger than 0!")
        self._rows = value
        
    @property
    def columns(self) -> int:
        """_summary_

        Returns:
            int: _description_
        """
        return self._columns
    
    @columns.setter
    def columns(self, value: int) -> None:
        """_summary_

        Args:
            value (int): _description_

        Raises:
            Exception: _description_
        """
        if value < 1:
            raise ValueError("Columns value should be bigger than 0!")
        self._columns = value

    @property
    def size(self) -> tuple[int, int]:
        """_summary_

        Returns:
            tuple[int, int]: _description_
        """
        return self.rows, self.columns

    @size.setter
    def size(self, value: tuple[int, int]) -> None:
        """_summary_

        Args:
            value (tuple[int, int]): _description_
        """
        self.rows, self.columns = value

    def is_within_bounds(self, row: int, column: int) -> bool:
        """_summary_

        Args:
            row (int): _description_
            column (int): _description_

        Returns:
            bool: _description_
        """
        return 0 <= row < self.rows and 0 <= column < self.columns

    def get_neighbors(self, row: int, column: int) -> list[tuple[int, int]]:
        """_summary_

        Args:
            row (int): _description_
            column (int): _description_

        Returns:
            list[tuple[int, int]]: _description_
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
        """_summary_

        Returns:
            dict[Cell, int]: _description_
        """
        cells_counter = {cell: 0 for cell in Cell}
        for row in self.grid:
            for cell in row:
                cells_counter[cell] += 1
        return cells_counter
    
    def reset(self) -> None:
        """_summary_
        """
        for row in self.grid:
            row[:] = [Cell.EMPTY] * len(row)
        self.enclosure_modified_cells.clear()

    def __str__(self) -> str:
        """_summary_

        Returns:
            str: _description_
        """
        number_of_columns = len(self.grid[0])
        max_width = 3 * len(str(number_of_columns)) + number_of_columns + 1
        line_str = "-" * max_width + "\n"
        
        grid_str = line_str
        for row in self.grid:
            row_str = " | ".join(str(cell.value) for cell in row)
            grid_str += "| " + row_str + " |\n"
            grid_str += line_str

        return grid_str.strip()

    def __getitem__(self, position: tuple[int, int]) -> Cell:
        """_summary_

        Args:
            position (tuple[int, int]): _description_

        Returns:
            Cell: _description_
        """
        row, column = position
        return self.grid[row][column]

    def __setitem__(self, position: tuple[int, int], value: Cell) -> None:
        """_summary_

        Args:
            position (tuple[int, int]): _description_
            value (Cell): _description_
        """
        row, column = position
        self.grid[row][column] = value

class GameModel:
    """
    Encapsulates the complete game state.
    Holds the board, players, and current active player.
    Acts as a structured container for all mutable game data.
    """

    def __init__(self, board: Board, *players: list[Player]) -> None:
        """_summary_

        Args:
            board (Board): _description_
            players (list[Player]): _description_
        """
        self.board = board
        self.players = players

        # Storing current player index
        self.current_player_index = 0
        
        # Mapping between Cell and Player
        self.cell_to_player = {}

        # In case we might need it in the future
        self.actions_history: dict[Cell, list[tuple[int, int]]] = {player.cell: [] for player in players}

        self._assign_cell_identities()
        self._assign_initial_positions()
        self._assign_initial_turn()

    def _assign_initial_turn(self) -> None:
        """_summary_
        """
        self.current_player_index = randint(0, len(self.players)-1)

    def _assign_initial_positions(self) -> None:
        """_summary_
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
            else:
                raise Exception(
                    "[GameModel._assign_initial_positions] An error occured: There are more players than available positions"
                )

    def _assign_cell_identities(self) -> None:
        """_summary_

        Raises:
            Exception: _description_
        """
        cells = list(Cell)[1:]
        if len(cells) < len(self.players):
            raise Exception(
                "[GameModel._assign_cell_identities] An error occured: There are more players than identities"
            )

        for i in range(len(self.players)):
            self.players[i].cell = cells[i]
            self.cell_to_player[cells[i]] = self.players[i]

    def assign_position(self, player: Player, position: tuple[int, int]) -> None:
        """_summary_

        Args:
            player (Player): _description_
            position (tuple[int, int]): _description_
        """
        self.board[position] = player.cell
        self.actions_history.setdefault(player.cell, [])
        self.actions_history[player.cell].append(player.position)
        player.position = position

    def current_player(self) -> Player:
        """_summary_

        Returns:
            Player: _description_
        """
        return self.players[self.current_player_index]

    def reset(self) -> None:
        """_summary_
        """
        self.board.reset()
        self.actions_history.clear()
        self._assign_initial_positions()
        self._assign_initial_turn()

    def get_opponents(self) -> list[Player]:
        """_summary_

        Returns:
            list[Player, ...]: _description_
        """
        return [player for player in self.players if player != self.current_player()]
    