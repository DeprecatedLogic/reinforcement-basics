from pixel_kart.directions import Direction, DIRECTION_ORDER
from pixel_kart.cells import Cell, CELL_TO_COLOR
from pixel_kart.actions import Action, AVAILABLE_ACTIONS
from pixel_kart.colors import Color
from random import choice, random
from pixel_kart.qtable import SHARED_QTABLE
import logging
logger = logging.getLogger(__name__)

class Player:
    """
    Base class representing a participant within the game space.

    Tracks absolute identity details, spatial coordinate arrays, operational speeds, 
    and track checkpoint validation states. Offers static registries to manage global 
    namespace and color constraints across active players.
    """
    player_names_used = []
    duplicate_names_allowed = False # for testing purposes; False by default (recommended)
    player_colors_used = []
    duplicate_colors_allowed = False # for testing purposes; False by default (recommended)

    def __init__(self, name: str, color: Color) -> None:
        """
        Initialize a player with unique identity tags, safe speeds, and start line validation.

        Args:
            name (str): Unique identifier and display name string.
            color (Color): Unique visual identity color selection.

        Raises:
            Exception: If name or color parameters violate active global uniqueness registries.
        """
        if name in Player.player_names_used and not Player.duplicate_names_allowed:
            logger.error(f"Player name '{name}' already in use")
            raise Exception(f"The name '{name}' is already in use, please enter another name.")
        Player.player_names_used.append(name)

        if color in Player.player_colors_used and not Player.duplicate_colors_allowed:
            logger.error(f"Player color '{color}' already in use")
            raise Exception(f"The color '{color.value}' is already in use, please use another color.")
        Player.player_colors_used.append(color)

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
        Select an action uniformly at random from a collection of available choices.

        Args:
            actions (list[Action]): Collection of valid environment actions to evaluate.

        Returns:
            Action: Selected action component.
        """
        return choice(actions)
    
    def win(self) -> None:
        """
        Increment total victory tracking registers.
        """
        self.nb_wins += 1

    def lose(self) -> None:
        """
        Increment total loss tracking registers.
        """
        self.nb_losses += 1

    @staticmethod
    def clear_used_names() -> None:
        """
        Wipe out the global historical name registry tracking records.
        """
        Player.player_names_used.clear()

    @staticmethod
    def clear_used_colors() -> None:
        """
        Wipe out the global historical color registry tracking records.
        """
        Player.player_colors_used.clear()
    
    def reset_stats(self) -> None:
        """
        Wipe out total victory and loss historical counts for this instance.
        """
        logger.debug(f"Resetting stats for {self.name}")
        self.nb_wins = 0
        self.nb_losses = 0
    
    def reset_kart(self) -> None:
        """
        Reset velocity, direction, crash flags, and orientation markers to baseline values.
        """
        logger.debug(f"Resetting kart for {self.name}")
        self.direction_index = 1
        self.speed = 0
        self.crashed = False
        self.start_line = True
        self.checkpoint = False
        self.nb_turns = 0

    def reset(self) -> None:
        """
        Execute a complete sweep of lifetime metrics and physical kart spatial trackers.
        """
        self.reset_stats()
        self.reset_kart()

    @property
    def total_games(self) -> int:
        """
        Compute total games finalized under this identity.

        Returns:
            int: Total game instances recorded.
        """
        return self.nb_wins + self.nb_losses
    
    @property
    def row(self) -> int:
        """
        Get the 0-indexed matrix vertical row position coordinate.

        Returns:
            int: Vertical position index.
        """
        return self._row
    
    @row.setter
    def row(self, value: int) -> None:
        """
        Set the vertical row coordinate parameter.

        Args:
            value (int): Vertical coordinate index. Must be non-negative.

        Raises:
            ValueError: If coordinate points below 0 bounds.
        """
        if value < 0:
            logger.error(f"Invalid row value: {value}")
            raise ValueError("Row value must be bigger than 0!")
        self._row = value

    @property
    def column(self) -> int:
        """
        Get the 0-indexed matrix horizontal column position coordinate.

        Returns:
            int: Horizontal position index.
        """
        return self._column
    
    @column.setter
    def column(self, value: int) -> None:
        """
        Set the horizontal column coordinate parameter.

        Args:
            value (int): Horizontal coordinate index. Must be non-negative.

        Raises:
            ValueError: If coordinate points below 0 bounds.
        """
        if value < 0:
            logger.error(f"Invalid column value: {value}")
            raise ValueError("Column value must be bigger than 0!")
        self._column = value

    @property
    def color(self) -> Color:
        """
        Get the specific Color Enum instance tracking this player's asset visualization layer.

        Returns:
            Color: Active player presentation color flag.
        """
        return self._color

    @color.setter
    def color(self, value: Color) -> None:
        """
        Assign an identity configuration token to the player visual asset tracker.

        Args:
            value (Color): Target Color configuration enum element.

        Raises:
            TypeError: If parameter configuration does not conform to core Color classes.
        """
        if not isinstance(value, Color):
            logger.error(f"Invalid color type for player {self.name}: {type(value)}")
            raise TypeError("Cannot set player's color to a value of type other than Color")

        # In case we want to avoid players using terrain colors
        #if value in CELL_TO_COLOR.values():
        #    logger.error(f"Player {self.name} attempted to use environment colors")
        #    raise ValueError("Cannot set player's color to the same color as the environment (this ain't a stealth game)")

        self._color = value

    @property
    def position(self) -> tuple[int, int]:
        """
        Extract coordinates as a unified coordinate mapping sequence.

        Returns:
            tuple[int, int]: (row_index, column_index)
        """
        return self.row, self.column

    @position.setter
    def position(self, value: tuple[int, int]) -> None:
        """
        Set spatial coordinate assignments.

        Args:
            value (tuple[int, int]): Two-element tuple consisting of (row, column) values.

        Raises:
            ValueError: If incoming inputs fail type validations or dimension properties.
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
        Get absolute directional matrix offset indexes (0=North, 1=East, 2=South, 3=West).

        Returns:
            int: Integer index indicating current heading direction.
        """
        return self._direction_index

    @direction_index.setter
    def direction_index(self, value: int) -> None:
        """
        Set directional matrix heading tracking registers.

        Args:
            value (int): Destination orientation index value inside range bounds [0, 3].

        Raises:
            ValueError: If direction value escapes the required system range intervals.
        """
        if  value < 0 or value > 3:
            logger.error(f"Invalid direction index: {value}")
            raise ValueError("Direction index must be in the range [0, 3]")
        self._direction_index = value

    def __str__(self) -> str:
        """
        Format player attributes into human-readable string values.

        Returns:
            str: Identity string identifier matching user profile names.
        """
        return f"{self.name}"
    
class Human(Player):
    """
    Subclass representing human-operated agents utilizing interface input handlers.
    """

    def __init__(self, name: str, color: Color) -> None:
        """
        Initialize a user-controlled profile layout.

        Args:
            name (str): Unique identifier display name.
            color (Color): Unique visual component representation color token.
        """
        super().__init__(name, color)

class AI(Player):
    """
    Reinforcement learning model agent utilizing Temporal Difference tabular Q-Learning.

    Extracts sensory data structures, applies exploration strategy choices, 
    and handles standard or terminal state reward processing updates.
    """

    def __init__(
        self, name: str, color: Color,
        epsilon: float = 0.9, lr: float = 0.01, gamma: float = 0.9,
        training: bool = False
    ) -> None:
        """
        Initialize an automated agent with custom operational parameters.

        Args:
            name (str): Unique descriptive profile name.
            color (Color): Unique presentation identity color configuration token.
            epsilon (float, optional): Epsilon-greedy rate tracking exploration frequency. Defaults to 0.9.
            lr (float, optional): Alpha learning rate scalar weighting model weight modifications. Defaults to 0.01.
            gamma (float, optional): Discount scalar weighting long-term situational rewards. Defaults to 0.9.
            training (bool, optional): Boolean toggling model updating behaviors on or off. Defaults to False.
        """
        super().__init__(name, color)

        self.epsilon = epsilon
        self.lr = lr
        self.gamma = gamma
        self.previous_state = None
        self.previous_action = None
        self.previous_reward = 0
        self.training = training
        logger.debug(
            f"Created a PixelKart AI with the following parameters:\n\
            - Epsilon: {self.epsilon}\n\
            - Learning rate: {self.lr}\n\
            - Gamma: {self.gamma}\n\
            - Training mode: {self.training}"
        )

    def _extract_state(self, game_state: dict) -> tuple:
        """
        Compile dynamic positional attributes and context parameters into a unified hashable key string.

        Note:
            Combines current forward velocity, lap-validation markers, and raycasted vision data 
            into a unified observation snapshot used for state lookups.

        Args:
            game_state (dict): Active context map forwarded from orchestration objects.

        Returns:
            tuple: Composite observation state tracking mapping features:
                   (speed, start_line, checkpoint, vision_1, ..., vision_n)
        """
        board = game_state["board"]

        # Get the cells relative to the player's current direction up to a specified depth
        relative_vision_cells = board.get_relative_vision(self.row, self.column, self.direction_index, vision_depth=2)

        return (
            self.speed,
            self.start_line,
            self.checkpoint
        ) + relative_vision_cells

    def play(self, game_state: dict) -> Action:
        """
        Select an environment action using an epsilon-greedy strategy.

        Note:
            Exploratory steps select actions uniformly at random, while exploitative steps 
            query the shared Q-table and select the index mapping to the maximal expected return value.

        Args:
            game_state (dict): Active data structures mapping environmental board items.

        Returns:
            Action: Chosen operational steering action element.
        """
        current_state = self._extract_state(game_state)

        # Epsilon-Greedy Action selection (only in training mode)
        if self.training and random() < self.epsilon:
            # Pick a random valid action
            action = choice(AVAILABLE_ACTIONS)
            action_index = AVAILABLE_ACTIONS.index(action)
        else:
            # Pick the action with the highest Q-value for this state
            q_values = SHARED_QTABLE.get_state_values(current_state)
            max_q = max(q_values)

            # Find all actions tied for the highest Q-value and pick one randomly
            best_actions = [i for i, q in enumerate(q_values) if q == max_q]
            action_index = choice(best_actions)
            action = AVAILABLE_ACTIONS[action_index]

        # Save the current state and action for the Bellman update later
        self.previous_state = current_state
        self.previous_action = action_index

        return action

    def compute_reward(self, game_state: dict, response: dict) -> None:
        """
        Calculate directional environment rewards and apply updates via standard Bellman equations.

        Note:
            Time bleed modifiers are step-calculated based on vehicle velocity. Critical events 
            such as track collisions invoke standalone terminal updates and clear state buffers immediately.

        Args:
            game_state (dict): Context map details tracking world parameters.
            response (dict): Telemetry payload feedback tracking environmental shifts.
        """
        if not self.training or self.previous_state is None or self.previous_action is None:
            return

        checkpoint_acquired = response.get("checkpoint_acquired")
        has_completed_lap = response.get("has_completed_lap")
        is_cheating = response.get("is_cheating")
        #is_last_lap = game_state["laps_completed"][player] == game_state["laps_required"]

        # Extract the new state (s')
        current_state = self._extract_state(game_state)

        # Tiered time penalty, rewarding speed by punishing less
        if self.speed == 2:
            reward = -0.01 # tiny bleed for maximum speed
        elif self.speed == 1:
            reward = -0.05 # medium bleed for slow movement
        elif self.speed < 0:
            reward = -0.1 # penalty for reversing
        else:
            reward = -0.2 # heavy penalty for being completely stationary (self.speed == 0)

        # Instant terminal math for crashes
        if self.crashed:
            reward = -10
            old_q_values = SHARED_QTABLE.get_state_values(self.previous_state)
            old_q_value = old_q_values[self.previous_action]
            
            # Pure terminal penalty. No gamma, no future state.
            new_q_value = old_q_value + self.lr * (reward - old_q_value)
            SHARED_QTABLE.update_state_values(self.previous_state, self.previous_action, new_q_value)

            logger.debug(f"Rewarded {self.name} with: {reward} points (instant terminal for crashing)")
            return

        # Standard rewards
        if is_cheating:
            reward -= 10
        if checkpoint_acquired:
            reward += 5
        if has_completed_lap:
            reward += 10

        # Standard Bellman update
        old_q_values = SHARED_QTABLE.get_state_values(self.previous_state)
        old_q_value = old_q_values[self.previous_action]

        new_q_values = SHARED_QTABLE.get_state_values(current_state)
        max_new_q_value = max(new_q_values)
        
        new_q_value = old_q_value + self.lr * (reward + self.gamma * max_new_q_value - old_q_value)
        SHARED_QTABLE.update_state_values(self.previous_state, self.previous_action, new_q_value)
        logger.debug(f"Rewarded {self.name} with: {reward} points (standard reward)")

    def force_terminal_update(self) -> None:
        """
        Commit delayed game-over rewards into tables at match conclusion intervals.

        Note:
            Drops future lookup components (gamma terms) to evaluate absolute terminal states.
        """
        if not self.training or self.previous_state is None or self.previous_action is None:
            return

        if self.previous_reward == 0:
            return

        logger.debug(f"Flushing pending terminal reward: {self.previous_reward} points")

        old_q_values = SHARED_QTABLE.get_state_values(self.previous_state)
        old_q_value = old_q_values[self.previous_action]

        # For a terminal state, there are no future actions, so we drop the gamma * max(Q) term
        # We only apply the final pending reward (which contains the win/lose score)
        new_q_value = old_q_value + self.lr * (self.previous_reward - old_q_value)
        
        SHARED_QTABLE.update_state_values(self.previous_state, self.previous_action, new_q_value)
        self.previous_reward = 0

    def reset_kart(self) -> None:
        """
        Reset instance velocity states, track validations, and evaluation buffers to baseline values.
        """
        super().reset_kart()
        self.previous_reward = 0
        self.previous_action = None
        self.previous_state = None

    def win(self) -> None:
        """
        Handle victory criteria milestones and queue a positive bonus reward.
        """
        super().win()
        self.previous_reward += 20
        self.force_terminal_update()

    def lose(self) -> None:
        """
        Handle match loss events. (Negative reward updates are commented out in this version).
        """
        super().lose()
        self.previous_reward -= 20
        self.force_terminal_update()

    def next_epsilon(self, coefficient = 0.97, minimum_eps = 0.05) -> None:
        """
        Apply step decay modifiers to exploration frequencies.

        Args:
            coefficient (float, optional): Multiplicative factor shrinking tracking values. Defaults to 0.97.
            minimum_eps (float, optional): Hard limit baseline floor value constraints. Defaults to 0.05.
        """
        self.epsilon *= coefficient
        if self.epsilon < minimum_eps:
            self.epsilon = minimum_eps

        logger.debug(f"Epsilon for AI ({self.name} set to: {self.epsilon}")
