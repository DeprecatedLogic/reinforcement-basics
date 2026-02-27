from random import choice
from player import Player

class Board:
    """
    Represents the game grid and manages all board-related logic.
    Stores cell ownership, provides neighbor access, and handles enclosure detection (BFS).
    (Contains no turn logic or player flow control.)
    """
    
    def __init__(self, rows: int, columns: int):
        self.rows = rows
        self.columns = columns
        self.grid = [[0 for _ in range(columns)] for _ in range(rows)]
    
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

    def get_neighbors():
        pass

    def should_check_enclosure():
        # pre-check 1: did the player move into an empty cell?
        #   if not, skip enclosure check
        # pre-check 2: are all neighboring cells (except where we came from) empty?
        #   if yes, skip enclosure check.

        # if the above checks failed to return False (skip enclosure check), return True.
        pass

    def count_cells():
        pass

class GameModel:
    """
    Encapsulates the complete game state.
    Holds the board, players, and current active player.
    Acts as a structured container for all mutable game data.
    """

    def __init__(self, board: Board, players: tuple[Player, Player], *colors):
        self.board = board
        self.players = players
        self.current_player = choice(players)
        self.actions_history = {player: [] for player in players}

    def is_game_over(self):
        pass

    def reset(self):
        pass

    def color_cell(self, row: int, column: int, player: Player):
        pass

    def get_winner(self) -> Player | None:
        """Return the winning player if the game is over, otherwise None."""
        if not self.is_game_over():
            return None
        return self.players[0] if self.current_player == self.players[1] else self.players[1]

    def get_loser(self) -> Player | None:
        """Return the losing player if the game is over, otherwise None."""
        if not self.is_game_over():
            return None
        return self.current_player
