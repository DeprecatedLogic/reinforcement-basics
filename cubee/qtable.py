class QTable:
    def __init__(self, preloaded_table = None, num_actions: int = 4, default_value: float = 0.0):
        self.storage = preloaded_table if preloaded_table is not None else {}

        self.num_actions = num_actions
        self.default_value = default_value

    def get_state_values(self, state: tuple):
        return self.storage.setdefault(state, [self.default_value] * self.num_actions)

    def update_state_values(self, state: tuple, action_idx: int, value: float):
        self.get_state_values(state)
        self.storage[state][action_idx] = value

SHARED_QTABLE = QTable()