from cubee.cells import Cell
from cubee.actions import Action
from cubee.colors import Color
from random import choice
import readchar
import logging
logger = logging.getLogger(__name__)

class Player:
    """
    Represents a player in the game.

    Stores identity, position, color, and statistics.
    Defines the interface for choosing an action.
    """
    player_names_used = []

    def __init__(self, name: str, color: Color) -> None:
        """
        Initialize a player with a unique name and a valid color.

        Args:
            name (str): Display name of the player (must be unique).
            color (Color): Color assigned to the player.

        Raises:
            Exception: If the name is already in use.
        """
        if name in Player.player_names_used:
            logger.error(f"Player name '{name}' already in use")
            raise Exception(f"The name '{name}' is already in use, please enter another name.")
        Player.player_names_used.append(name)

        self.name = name
        self.color = color
        self.nb_wins = 0
        self.nb_losses = 0
        self.row = 0
        self.column = 0
        self.cell: Cell | None = None

    def play(self, actions: list[Action]) -> Action:
        """
        Select an action from the available ones.

        Args:
            actions (list[Action]): Valid actions for the current turn.

        Returns:
            Action: Chosen action.
        """
        return choice(actions)
    
    @staticmethod
    def clear_used_names() -> None:
        """
        Clear the registry of used player names.
        """
        Player.player_names_used.clear()
    
    def reset_stats(self) -> None:
        """
        Reset the player's statistics (wins and losses) and clear used names.
        """
        logger.debug(f"Resetting stats for {self.name}")
        self.nb_wins = 0
        self.nb_losses = 0
        Player.clear_used_names()

    @property
    def total_games(self) -> int:
        """
        Total number of games played by the player.

        Returns:
            int: Number of games played.
        """
        return self.nb_wins + self.nb_losses
    
    @property
    def row(self) -> int:
        """
        Get the player's row position.

        Returns:
            int: Row index (0-based)
        """
        return self._row
    
    @row.setter
    def row(self, value: int) -> None:
        """
        Set the player's row position.

        Args:
            value (int): New row index (0-based)

        Raises:
            ValueError: If value < 0.
        """
        if value < 0:
            logger.error(f"Invalid row value: {value}")
            raise ValueError("Row value must be bigger than 0!")
        self._row = value

    @property
    def column(self) -> int:
        """
        Get the player's column position.

        Returns:
            int: Column index (0-based)
        """
        return self._column
    
    @column.setter
    def column(self, value: int) -> None:
        """
        Set the player's column position.

        Args:
            value (int): New column index (0-based)

        Raises:
            ValueError: If value < 0.
        """
        if value < 0:
            logger.error(f"Invalid column value: {value}")
            raise ValueError("Column value must be bigger than 0!")
        self._column = value

    @property
    def color(self) -> Color:
        """
        Get the player's color.

        Returns:
            Color: Player's color.
        """
        return self._color

    @color.setter
    def color(self, value: Color) -> None:
        """
        Set the player's color.

        Args:
            value (Color): New color to assign.

        Raises:
            TypeError: If value is not a Color.
            ValueError: If value is Color.EMPTY.
        """
        if not isinstance(value, Color):
            logger.error(f"Invalid color type for player {self.name}: {type(value)}")
            raise TypeError("Cannot set player's color to a value of type other than Color")

        if value == Color.EMPTY:
            logger.error(f"Player {self.name} attempted to use EMPTY color")
            raise ValueError("Cannot set player's color to the same color as the empty cells")

        self._color = value

    @property
    def position(self) -> tuple[int, int]:
        """
        Get the player's current position.

        Returns:
            tuple[int, int]: (row, column)
        """
        return self.row, self.column

    @position.setter
    def position(self, value: tuple[int, int]) -> None:
        """
        Set the player's position.

        Args:
            value (tuple[int, int]): (row, column)

        Raises:
            ValueError: If value is not a tuple of two integers.
        """
        if not (
            isinstance(value, tuple) and len(value) == 2 and
            all(isinstance(element, int) for element in value)
        ):
            logger.error(f"Invalid position value for player {self.name}: {value}")
            raise ValueError("Position must be a tuple of two integers (row, column)")
        
        self.row, self.column = value

    def win(self):
        """_summary_
        """
        self.nb_wins += 1

    def lose(self):
        """_summary_
        """
        self.nb_losses += 1

    def __str__(self) -> str:
        """
        Return a string representation of the player.

        Returns:
            str: Player name and associated cell.
        """
        return f"{self.name}({self.cell.name})"
    
class Human(Player):
    """
    Player controlled by user input.

    Handles CLI input to select actions.
    """

    def __init__(self, name: str, color: Color) -> None:
        """
        Initialize a human player.

        Args:
            name (str): Player name.
            color (Color): Player color.
        """
        super().__init__(name, color)

    def play(self, actions: list[Action]) -> Action:
        """
        Prompt the user to choose an action via keyboard input.
        
        Args:
            actions (list[Action]): Valid actions for the current turn.

        Returns:
            Action: Selected action.
        """
        while True:
            try:
                print(f"Press key for action (WASD): ", end="", flush=True)
                key = readchar.readkey().strip().lower()
                action_taken = Action.KEY_TO_ACTION.get(key)
                if action_taken and action_taken in actions:
                    logger.debug(f"Key pressed: {key}")
                    return action_taken
                else:
                    print("Invalid input, try again")
            except Exception as e:
                logger.error(f"Unexpected error in Human.play: {e}")
                print(f"[Human.play] An unexpected error occured: {e}")