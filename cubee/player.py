from cubee.cell import Cell
from cubee.actions import Action
from random import choice

class Player:
    """
    Represents a generic player of the game.
    Stores identity and statistics (wins/losses) and defines the interface for choosing an action.
    """

    def __init__(self, name) -> None:
        """
        Initialize a new player.

        Args:
            name: The player's display name
            position: The player's position, row & column.

        Note:
            The parameter `position` should contain the row and column, not x and y.
        """
        self.name = name
        self.nb_wins = 0
        self.nb_losses = 0
        self.row = 0
        self.column = 0
        self.cell: Cell | None = None

    def play(actions: list[Action]) -> Action:
        """
        Play description.
        
        Args:
            actions: The actions a player can take in the current situation.

        Returns:
            The action taken by the player.
        """
        return choice(actions)

    def reset_stats(self) -> None:
        """ reset_stats description """
        self.nb_wins = 0
        self.nb_losses = 0
    
    @property
    def nb_games(self) -> int:
        """ Return the total number of games played by the player. """
        return self.nb_wins + self.nb_losses
    
class Human(Player):
    """
    Player controlled by user input (CLI or GUI).
    Overrides the play method to request and validate user input.
    """
    
    def __init__(self, name):
        super().__init__(name)

    def play(self, actions: list[Action]) -> Action:
        """
        Prompt the human player for the action to take.

        Note:
            Only called if the game is being played in CLI mode.

        Args:
            actions: The actions a player can take in the current situation.
            
        Returns:
            The action the player took.
        """
        while True:
            try:
                action_taken = Action(input(
                    f"Enter the desired action (available: {','.join([action.name for action in actions])}): "
                ).upper().strip())
                return action_taken
            except KeyError:
                print(f"[Player.play] Invalid input, try again")
            except Exception as e:
                print(f"[Player.play] An uncaught error occured: {e}")

class AI(Player):
    """
    Automated Player.
    """

    def __init__(self, name):
        super().__init__(name)
