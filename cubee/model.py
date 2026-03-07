from random import choice
from cubee.player import Player
from cubee.actions import Action
from cubee.cell import Cell

class Board:
    """
    Represents the game grid and manages all board-related logic.
    Stores cell ownership, provides neighbor access, and handles enclosure detection (BFS).
    (Contains no turn logic or player flow control.)
    """
    
    def __init__(self, rows: int, columns: int):
        self.rows = rows
        self.columns = columns
        self.grid = [[Cell.EMPTY for _ in range(columns)] for _ in range(rows)]
    
    @property
    def rows(self) -> int:
        return self._rows
    
    @rows.setter
    def rows(self, value):
        if value < 1:
            raise Exception("Rows value should be bigger than 0!")
        self._rows = value
        
    @property
    def columns(self) -> int:
        return self._columns
    
    @columns.setter
    def columns(self, value):
        if value < 1:
            raise Exception("Columns value should be bigger than 0!")
        self._columns = value

    def is_within_bounds(self, row: int, column: int) -> bool:
        return 0 <= row < self.rows and 0 <= column < self.columns

    def get_neighbors(self, row: int, column: int) -> list[tuple[int, int]]:
        neighbors = []

        deltas = [action.value for action in tuple(Action)]
        for delta in deltas:
            delta_row, delta_column = delta
            neighbor_row = row + delta_row
            neighbor_column = column + delta_column

            if self.is_within_bounds(neighbor_row, neighbor_column):
                neighbors.append((neighbor_row, neighbor_column))
                
        return neighbors

    def should_check_enclosure(self):
        # pre-check 1: did the player move into an empty cell?
        #   if not, skip enclosure check
        # pre-check 2: are all neighboring cells (except where we came from) empty?
        #   if yes, skip enclosure check.

        # if the above checks failed to return False (skip enclosure check), return True.
        pass

    def check_enclosure(self):
        """ BFS implementation """
        pass

    def count_cells(self) -> dict[Cell, int]:
        """ count_cells description """
        cells_counter = {
            Cell.EMPTY: 0,
            Cell.P1: 0,
            Cell.P2: 0
        }
        for row in self.grid:
            for cell in row:
                cells_counter[cell] += 1
        return cells_counter
    
    def reset(self) -> None:
        self.grid = [[Cell.EMPTY for _ in range(self.columns)] for _ in range(self.rows)]

class GameModel:
    """
    Encapsulates the complete game state.
    Holds the board, players, and current active player.
    Acts as a structured container for all mutable game data.
    """

    def __init__(self, board: Board, players: tuple[Player, Player]) -> None:
        self.board = board
        self.players = players
        self.current_player = choice(players)
        
        self._assign_cell_identities()
        self._assign_initial_positions()
        
        self.actions_history: dict[Cell, list[tuple[int, int]]] = {player.cell: [] for player in players}

    def _assign_initial_positions(self) -> None:
        player1, player2 = self.players
        player1.row, player1.column = (0, 0)
        player2.row, player2.column = (self.board.rows-1, self.board.columns-1)

    def _assign_cell_identities(self) -> None:
        self.players[0].cell = Cell.P1
        self.players[1].cell = Cell.P2

    def is_game_over(self) -> bool:
        """ is_game_over description """
        return self.board.count_cells()[Cell.EMPTY] == 0

    def move_player(self, player: Player, row, column):
        self.actions_history[player.cell].append((player.row, player.column))
        player.row = row
        player.column = column

    def reset(self) -> None:
        """ reset description """
        self.board.reset()
        self.actions_history.clear()
        self.current_player = choice(self.players)

    def get_opponent(self) -> Player:
        """ get_opponent description """
        return self.players[1] if self.current_player == self.players[0] else self.players[0]
    