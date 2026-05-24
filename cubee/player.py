from cubee.cells import Cell
from cubee.actions import Action, ACTION_TO_INDEX
from cubee.colors import Color
from random import choice, random
import readchar
from cubee.qtable import SHARED_QTABLE
#from contextlib import contextmanager
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
        """
        super().__init__(name, color)

        self.epsilon = epsilon
        self.lr = lr
        self.gamma = gamma
        self.previous_state = None
        self.previous_action = None
        self.last_reward = 0
        self.nb_cells = 1 # every player starts with at least 1 cell
        self.training = True
        logger.debug(
            f"Created a Cubee AI with the following parameters:\n\
            - Epsilon: {self.epsilon}\n\
            - Learning rate: {self.lr}\n\
            - Gamma: {self.gamma}\n\
            - Training mode: {self.training}"
        )

    def play(self, game_state: dict):
        valid_actions = game_state["valid_actions"]
        me: AI = game_state["current_player"]
        opponents = game_state["opponents"]
        state = me.position
        for opponent in opponents:
            state += opponent.position

        if self.training:
            if self.previous_state is not None:
                # Get old Q value for formula
                prev_q_values = SHARED_QTABLE.get_state_values(self.previous_state)
                prev_index = ACTION_TO_INDEX[self.previous_action]
                old_value = prev_q_values[prev_index]

                # Get max Q value for current state (best future value)
                current_q_values = SHARED_QTABLE.get_state_values(state)
                max_next = max(current_q_values)

                # Q-learning formula Q(s,a)← Q(s,a)+α[r+γ*maxa′​Q(s′,a′)−Q(s,a)] => old Q value + learning rate *(reward + gamma * max_next - old Q value)
                new_value = old_value + self.lr * (self.last_reward + self.gamma * max_next - old_value)

                # Store updated value
                SHARED_QTABLE.update_state_values(self.previous_state, prev_index, new_value)

        q_values = SHARED_QTABLE.get_state_values(state)

        best_value = float('-inf')
        best_action = None
            
        if random() < self.epsilon:
            best_action = choice(valid_actions)
        else:
            for action in valid_actions:
                index = ACTION_TO_INDEX[action]
                value = q_values[index]

                if value > best_value:
                    best_action = action
                    best_value = value

        self.previous_state = state
        self.previous_action = best_action

        return best_action
    
    def compute_reward(self, game_state: dict, response: dict) -> None:
        """
        Compute and update the reward signal based on the latest game transition.

        The reward is primarily derived from the number of cells gained during the move.
        An additional bonus is applied when an enclosure occurs, scaled proportionally
        to the board size.

        Args:
            game_state (dict): Current game state containing board dimensions and context.
            response (dict): Result of the last action, including:
                - "nb_cells_gained" (int): Number of cells captured.
                - "enclosure_modified_cells" (list): Cells affected by an enclosure.
        """
        reward = response["nb_cells_gained"]

        # Enclosure bonuses
        board_size = game_state["board_rows"] * game_state["board_columns"]
        ratio = reward / board_size
        enclosure_reward_value = int(50 * ratio) # For natural scaling instead of random numbers

        if len(response["enclosure_modified_cells"]) > 0:
            reward += enclosure_reward_value

    def win(self) -> None:
        """
        Handle a win event and update the reward signal.

        Increments the win counter and applies a positive reward bonus.
        """
        super().win()
        self.last_reward += 10

    def lose(self) -> None:
        """
        Handle a loss event and update the reward signal.

        Increments the loss counter and applies a negative reward penalty.
        """
        super().lose()
        self.last_reward -= 10

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
