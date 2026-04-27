from pixel_kart.cells import Cell, CELL_TO_COLOR
from pixel_kart.actions import Action
from pixel_kart.colors import Color
from random import choice, random
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
        
        self.direction_index = 1 # East by default
        self.speed = 0
        self.crashed = False
        self.start_line = True
        self.checkpoint = False
        self.nb_turns = 0

    def play(self, actions: list[Action]) -> Action:
        """
        Select an action from the available ones.

        Args:
            actions (list[Action]): Valid actions for the current turn.

        Returns:
            Action: Chosen action.
        """
        return choice(actions)
    
    def win(self):
        self.nb_wins += 1

    def lose(self):
        self.nb_losses += 1

    @staticmethod
    def clear_used_names() -> None:
        """
        Clear the registry of used player names.
        """
        Player.player_names_used.clear()
    
    def reset_stats(self) -> None:
        """
        Reset the player's statistics.
        """
        logger.debug(f"Resetting stats for {self.name}")
        self.nb_wins = 0
        self.nb_losses = 0
    
    def reset_kart(self) -> None:
        """
        Reset the player's kart attributes.
        """
        logger.debug(f"Resetting kart for {self.name}")
        self.direction_index = 1
        self.speed = 0
        self.crashed = False
        self.start_line = True
        self.checkpoint = False
        self.nb_turns = 0

    def reset(self) -> None:
        self.reset_stats()
        self.reset_kart()

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

        if value in CELL_TO_COLOR.values():
            logger.error(f"Player {self.name} attempted to use environment colors")
            raise ValueError("Cannot set player's color to the same color as the environment (this ain't a stealth game)")

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

    @property
    def direction_index(self) -> int:
        """
        _summary_

        Returns:
            int: _description_
        """
        return self._direction_index

    @direction_index.setter
    def direction_index(self, value: int) -> None:
        """
        _summary_

        Args:
            value (int): _description_
        """
        if  value < 0 or value > 3:
            logger.error(f"Invalid direction index: {value}")
            raise ValueError("Direction index must be in the range [0, 3]")
        self._direction_index = value

    def __str__(self) -> str:
        """
        Return a string representation of the player.

        Returns:
            str: Player name and associated cell.
        """
        return f"{self.name}"
    
class Human(Player):
    """
    Player controlled by user input.
    """

    def __init__(self, name: str, color: Color) -> None:
        """
        Initialize a human player.

        Args:
            name (str): Player name.
            color (Color): Player color.
        """
        super().__init__(name, color)

class AI(Player):
    """
    Automated player controlled by AI logic.
    """

    def __init__(self, name: str, color: Color, epsilon: float = 0.9, lr: float = 0.01, gamma: float = 0.9, training: bool = True) -> None:
        """
        Initialize an AI player.

        Args:
            name (str): Player name.
            color (Color): Player color.
            epsilon (float, optional): _description_. Defaults to 0.9.
            lr (float, optional): _description_. Defaults to 0.01.
            gamma (float, optional): _description_. Defaults to 0.9.
            training (bool, optional): _description_. Defaults to True.
        """
        super().__init__(name, color)

        self.epsilon = epsilon
        self.lr = lr
        self.gamma = gamma
        self.previous_state = None
        self.previous_action = None
        self.training = True
        logger.debug(
            f"Created an AI with the following parameters:\n\
            - Epsilon: {self.epsilon}\n\
            - Learning rate: {self.lr}\n\
            - Gamma: {self.gamma}\n\
            - Training mode: {self.training}"
        )

    def play(self, game_state: dict):
        pass

    def next_epsilon(self, coefficient = 0.95, minimum_eps = 0.05) -> None:
        """
        Reduce the exploration rate (epsilon decay).

        Args:
            coefficient: Multiplicative decay factor (should be < 1)
            minimum_eps: Floor value below which epsilon will not decrease
        """
        self.epsilon *= coefficient
        if self.epsilon < minimum_eps:
            self.epsilon = minimum_eps

        logger.debug(f"Epsilon for AI ({self.name}, {self.cell.name}) set to: {self.epsilon}")
