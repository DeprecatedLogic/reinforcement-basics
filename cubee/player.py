from random import choice

class Player:
    """
    Represents a generic player of the game.
    Stores identity and statistics (wins/losses) and defines the interface for choosing an action.
    """

    def __init__(self, name):
        """
        Initialize a new player.

        Args:
            name: The player's display name
        """
        self.name = name
        self.nb_wins = 0
        self.nb_losses = 0
        pass

    @staticmethod
    def play(actions_available: list):
        """
        Play description.
        
        Args:
            actions_available: The actions a player can take in the current situation.

        Returns:
            The action taken by the player.
        """
        return choice(actions_available)
    
    @property
    def nb_games(self) -> int:
        """Return the total number of games played by the player."""
        return self.nb_wins + self.nb_losses
    
class Human(Player):
    """
    Player controlled by user input (CLIR or GUI).
    Overrides the play method to request and validate user input.
    """
    
    def __init__(self, name):
        super().__init__(name)

    def play(self, actions_available: list) -> int:
        """
        Prompt the human player for the number of matches to remove.

        Note:
            Only called if the game is being played in CLI mode.

        Args:
            actions_available: The actions a player can take in the current situation.
            
        Returns:
            Valid number of matches to .
        """
        while True:
            action_taken = input(
                f"Enter the desired action (available: {str(actions_available).strip('[]')}): "
            )
            if action_taken in actions_available:
                return action_taken
            
            print("Invalid Entry!")

class AI(Player):
    """
    Automated Player.
    """

    def __init__(self, name):
        super().__init__(name)
