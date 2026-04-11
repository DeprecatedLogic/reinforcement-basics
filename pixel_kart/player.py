from abc import ABC, abstractmethod
import random
from pixel_kart.model import Kart, Direction, DIRECTIONS, DIR_ORDER

class Player(ABC):
    def __init__(self, name: str, color: str = "red"):
        self.name = name
        self.color = color

    @abstractmethod
    def choose_action(self, kart: Kart, circuit) -> str:
        """Return one of: 'acc', 'brake', 'left', 'right', 'nothing'"""
        # TODO: Remove random player and use Player as random
        pass

class HumanPlayer(Player):
    def choose_action(self, kart: Kart, circuit) -> str:
        # Controlled via GUI buttons
        raise NotImplementedError("Human uses GUI")

class RandomAIPlayer(Player):
    def choose_action(self, kart: Kart, circuit) -> str:
        actions = ['acc', 'brake', 'left', 'right', 'nothing']
        return random.choice(actions)

class AI(Player):
    pass