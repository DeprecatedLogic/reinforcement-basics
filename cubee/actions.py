from enum import Enum

class Action(Enum):
    UP = (-1, 0)
    RIGHT = (0, 1)
    DOWN = (1, 0)
    LEFT = (0, -1)

    @property
    def delta(self):
        return self.value
