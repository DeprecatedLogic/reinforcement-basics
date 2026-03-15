from cubee.cells import Cell
from cubee.actions import Action
from cubee.colors import Color
from random import choice

class Player:
    """
    Represents a generic player of the game.
    Stores identity and statistics (wins/losses) and defines the interface for choosing an action.
    """
    player_names_used = []

    def __init__(self, name: str, color: Color):
        """
        Initialize a new player.

        Args:
            name (str): The player's display name
            color (str): The player's color

        Note:
            The parameter `position` should contain the row and column, not x and y.
        """
        if name in Player.player_names_used:
            raise Exception(f"The name '{name}' is already in use, please enter another name.")
        self.name = name
        self.color = color
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
    def total_games(self) -> int:
        """Return the total number of games played by the player.

        Returns:
            _type_: _description_
        """
        return self.nb_wins + self.nb_losses
    
    @property
    def color(self) -> None:
        """_summary_

        Returns:
            _type_: _description_
        """
        return self._color

    @color.setter
    def color(self, value: Color) -> None:
        """_summary_

        Args:
            value (Color): _description_

        Raises:
            Exception: _description_

        Returns:
            _type_: _description_
        """
        if not isinstance(value, Color):
            raise TypeError("Cannot set player's color to a value of type other than Color")

        if value == Color.EMPTY:
            raise ValueError("Cannot set player's color to the same color as the empty cells")

        self._color = value

    @property
    def position(self) -> tuple[int, int]:
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.row, self.column

    @position.setter
    def position(self, value: tuple[int, int]) -> None:
        """_summary_

        Args:
            value (tuple[int, int]): _description_
        """
        if not (
            isinstance(value, tuple) and len(value) == 2 and
            all(isinstance(element, int) for element in value)
        ):
            raise ValueError("What the F are you doing ? Take a break, drink a coffee, you need it.")
        
        self.row, self.column = value

    def __str__(self) -> str:
        """Return a string representation of self."""
        return f"{self.name}({self.cell.name})"
    
class Human(Player):
    """
    Player controlled by user input (CLI or GUI).
    Overrides the play method to request and validate user input.
    """
    
    def __init__(self, name: str, color: Color):
        super().__init__(name, color)

    def play(self, actions: list[Action]) -> Action:
        """
        Prompt the human player for the action to take.

        Note:
            Only called if the game is being played in CLI mode.

        Args:
            actions (list[Action]): The actions a player can take in the current situation.
            
        Returns:
            Action: The action the player took.
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

    def __init__(self, name: str, color: Color):
        super().__init__(name, color)
