import logging
logger = logging.getLogger(__name__)

class QTable:
    """
    In-memory lookup table storing state-action utility metrics for Reinforcement Learning.

    Manages expected cumulative future reward vectors (Q-values) indexed by composite 
    observation state tuples. Provides dynamic initialization fallbacks for previously 
    unseen state coordinates.
    """

    def __init__(self, preloaded_table = None, num_actions: int = 5, default_value: float = 0.0) -> None:
        """
        Initialize the Q-table storage dictionary and dimensional action boundaries.

        Args:
            preloaded_table (dict, optional): An existing mapping dictionary containing 
                                             historical state-action vectors. Defaults to None.
            num_actions (int, optional): The total number of valid operational actions available 
                                         per environment state. Defaults to 5.
            default_value (float, optional): Baseline floating-point initialization value assigned 
                                             to unmapped state entries. Defaults to 0.0.
        """
        self.storage = preloaded_table if preloaded_table is not None else {}

        self.num_actions = num_actions
        self.default_value = default_value

    def get_state_values(self, state: tuple) -> list:
        """
        Retrieve the collection of action values associated with a specific observation state.

        Note:
            If the queried state tuple does not exist in the collection, it is dynamically 
            instantiated as a flat list populated with `default_value` elements matching 
            the count constraint defined by `num_actions`.

        Args:
            state (tuple): The composite observation features mapping used as the lookup key.

        Returns:
            list[float]: A sequence of Q-values mapping sequentially to available discrete actions.
        """
        return self.storage.setdefault(state, [self.default_value] * self.num_actions)

    def update_state_values(self, state: tuple, action_index: int, value: float) -> None:
        """
        Assign a calculated target value to a explicit state-action coordinate block.

        Note:
            Guarantees key presence prior to value assignments by invoking `get_state_values` 
            internally to perform fallback entry configuration if required.

        Args:
            state (tuple): The target observation feature tracking matrix key.
            action_index (int): Array offset index identifying the modified environmental action.
            value (float): The newly computed utility metric to record.
        """
        self.get_state_values(state)
        self.storage[state][action_index] = value

    def __str__(self) -> str:
        """
        Format the tracking storage mapping matrix into an explicit newline-delimited table.

        Returns:
            str: Normalized display presentation tracking every recorded state configuration row.
        """
        result = []
        for state in self.storage.keys():
            result.append(f"{state} ")
            values = self.storage[state]
            values = ' | '.join(str(value) for value in values)
            result.append(values + "\n")

        return ''.join(result)

SHARED_QTABLE = QTable()