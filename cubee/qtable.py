import logging
logger = logging.getLogger(__name__)

class QTable:
    def __init__(self, preloaded_table = None, num_actions: int = 4, default_value: float = 0.0):
        self.storage = preloaded_table if preloaded_table is not None else {}

        self.num_actions = num_actions
        self.default_value = default_value

    def get_state_values(self, state: tuple):
        return self.storage.setdefault(state, [self.default_value] * self.num_actions)

    def update_state_values(self, state: tuple, action_index: int, value: float):
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

SHARED_QTABLE = QTable()