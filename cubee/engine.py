from cubee.player import Player
from cubee.model import GameModel
from cubee.actions import Action
from cubee.cell import Cell

class GameEngine:
    """
    Implements the rules and flow of the game.
    Validates moves, updates the board through the model, triggers enclosure detection when required,
        switches turns, and determines game outcome.
    (Contains no UI logic.)
    """
    
    def __init__(self, model: GameModel):
        self.model = model

    def is_valid_action(self, action: Action):
        """
        is_valid_action description
        """
        board = self.model.board

        # Calculate the delta between player's position and action taken
        delta_row, delta_column = action.delta
        player_row = self.model.current_player.row + delta_row
        player_column = self.model.current_player.column + delta_column

        # Check if we're moving out of bounds or onto opponent's territory
        if not board.is_within_bounds(player_row, player_column):
            print(f"[GameEngine.is_valid_action] Action '{action.name}' is out of bounds")
            return False
        if board.grid[player_row][player_column] == self.model.get_opponent().cell:
            print(f"[GameEngine.is_valid_action] Action '{action.name}' is invalid, cannot move onto opponent's territory")
            return False
        
        return True
        
    def make_move(self):
        """
        make_move description
        """

        # Filter only valid actions
        actions_available = [action for action in list(Action) if self.is_valid_action(action)]
        
        # player plays then we switch
        action_taken = self.model.current_player.play(actions_available)

        self.switch_player()

    def switch_player(self) -> None:
        """Get the next player."""
        players = self.model.players
        current_player = self.model.current_player
        if current_player == players[0]:
            current_player = players[1]
        else:
            current_player = players[0]

    def get_winner(self) -> Player | None:
        """ Return the winning player if the game is over, otherwise None. """
        if not self.model.is_game_over():
            return None
        
        player1, player2 = self.model.players
        cells_counter = self.model.board.count_cells()
        return player1 if cells_counter[Cell.P1] > cells_counter[Cell.P2] else player2

    def get_loser(self) -> Player | None:
        """ Return the losing player if the game is over, otherwise None. """
        if not self.model.is_game_over():
            return None
        
        player1, player2 = self.model.players
        cells_counter = self.model.board.count_cells()
        return player1 if cells_counter[Cell.P1] < cells_counter[Cell.P2] else player2
    