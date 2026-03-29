from cubee.qtable import SHARED_QTABLE
from random import choice, random
from math import inf
from cubee.actions import ACTION_TO_INDEX
from cubee.colors import Color
from cubee.player import Player
from cubee.model import GameModel
import logging
logger = logging.getLogger(__name__)

class AI(Player):
    """
    Automated player controlled by AI logic.
    """
    def __init__(self, name: str, color: Color, epsilon: float = 0.9, lr: float = 0.01, gamma: float = 0.9) -> None:
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

    def play(self, model: GameModel, valid_actions: list|tuple):
        
        state = (model.current_player().position, tuple(opp.position for opp in model.get_opponents()))

        if self.previous_state is not None:
            # Get old Q value for formula
            prev_q_values = SHARED_QTABLE.get_state_values(self.previous_state)
            prev_idx = ACTION_TO_INDEX[self.previous_action]
            old_value = prev_q_values[prev_idx]

            # Get max Q value for current state (best future value)
            current_q_values = SHARED_QTABLE.get_state_values(state)
            max_next = max(current_q_values)

            # Q-learning formula Q(s,a)← Q(s,a)+α[r+γ*maxa′​Q(s′,a′)−Q(s,a)] => old Q value + learning rate *(reward + gamma * max_next - old Q value)
            new_value = old_value + self.lr * (self.last_reward + self.gamma * max_next - old_value)

            # Store updated value
            SHARED_QTABLE.update_state_values(self.previous_state, prev_idx, new_value)

        q_values = SHARED_QTABLE.get_state_values(state)

        best_value = -inf
        best_action = None
            
        if random() < self.epsilon:
            best_action = choice(valid_actions)
        else:
            for action in valid_actions:
                idx = ACTION_TO_INDEX[action]
                value = q_values[idx]

                if value > best_value:
                    best_action = action
                    best_value = value

        self.previous_state = state
        self.previous_action = best_action

        return best_action
    
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