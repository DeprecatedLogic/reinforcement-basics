import logging
logger = logging.getLogger(__name__)

class QTable:
    def __init__(self, preloaded_table = None, num_actions: int = 4, default_value: float = 0.0):
        self.storage = preloaded_table if preloaded_table is not None else {}

        self.num_actions = num_actions
        self.default_value = default_value

    def get_state_values(self, state: tuple) -> list:
        """
        Retrieve the Q-values associated with a given state.

        Note:
            If the state is not already present in the table, it is initialized
            with a list of default values (one per action) and then returned.

        Args:
            state (tuple): The Q-table state.

        Returns:
            list: List of Q-values corresponding to all possible actions for the state.
        """
        return self.storage.setdefault(state, [self.default_value] * self.num_actions)

    def update_state_values(self, state: tuple, action_index: int, value: float) -> None:
        """
        Update the Q-value for a given state-action pair.

        Note:
            If the state does not exist in the table, it is initialized with default values.

        Args:
            state (tuple): The Q-table state.
            action_index (int): Index of the action to update.
            value (float): New Q-value to assign for the given state-action pair.
        """
        self.get_state_values(state)
        self.storage[state][action_index] = value

    def __str__(self):
        result = []
        for state in self.storage.keys():
            result.append(f"{state} ")
            values = self.storage[state]
            values = ' | '.join(str(value) for value in values)
            result.append(values + "\n")

        return ''.join(result)
