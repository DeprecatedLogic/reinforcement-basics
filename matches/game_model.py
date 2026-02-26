from random import randint
from matches.player import Player
import json

class GameModel():
    """Core game logic framework."""
    def __init__(self, nb: int, player1 : Player, player2 : Player, displayable: bool = True):
        """
        Create a new game instance.

        Args:
            nb: Starting number of matches
            player1: First possible player
            player2: Second possible player
            displayable: Whether console output should be shown during play()
        """
        self.nb = nb
        self.original_nb = nb
        self.displayable = displayable
        self.players = [player1, player2]

        player1.game = self
        player2.game = self

        self.current_player = None
        self.shuffle()

    def display(self, player_name: str) -> None:
        """Print current game state to console if displayable is True."""
        if self.displayable:
            print(f"Remaining matches: {self.nb}")
            print(f"It is {player_name}'s turn.")

    def step(self, action: int) -> None:
        """
        Execute a move by removing the specified number of matches.

        Args:
            action: Number of matches to remove

        Raises:
            ValueError: If the action is invalid (out of range or too large)
        """
        if action < 1 or action > 3 or action > self.nb:
            raise ValueError("Action invalide")
        self.nb -= action

    def shuffle(self) -> None:
        """Randomly select which player starts the game."""
        self.current_player = self.players[randint(0, 1)]

    def reset(self) -> None:
        """Restore initial number of matches and randomly re-assign starting player."""
        self.nb = self.original_nb
        self.shuffle()

    def switch_player(self) -> None:
        """Get the next player in turn."""
        if self.current_player == self.players[0]:
            self.current_player = self.players[1]
        else:
            self.current_player = self.players[0]

    def is_game_over(self) -> bool:
        """Check if the game has ended (no matches remaining)."""
        return self.nb <= 0

    def get_current_player(self) -> Player:
        """Return the player whose turn it is currently."""
        return self.current_player

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
    
    def get_remaining_matches(self) -> int:
        """Return the current number of matches left."""
        return self.nb
    
    def play(self) -> None:
        """
        Run one complete console-based game until a winner is determined.
        Updates player statistics automatically at the end.
        """
        while not self.is_game_over():
            current_player = self.get_current_player()
            self.display(current_player.name)
            
            action = current_player.play()
            action = min(action, self.nb)
            
            self.step(action)
            
            if self.is_game_over():
                break
            
            self.switch_player()
        
        winner = self.get_winner()
        loser = self.get_loser()
        if winner and loser:
            winner.win()
            loser.lose()