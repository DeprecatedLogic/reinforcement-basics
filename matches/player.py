from random import randint

class Player():
    def __init__(self, name: str, game = None):
        self.name = name
        self.nb_wins = 0
        self.nb_losses = 0
        self.game = game

    @staticmethod
    def play():
        return randint(1, 3)
        
    @property
    def nb_games(self):
        return self.nb_wins + self.nb_losses

    def win(self):
        self.nb_wins += 1

    def lose(self):
        self.nb_losses += 1

    def __str__(self):
        return f"{self.name} has {self.nb_wins} victories and {self.nb_losses} losses in {self.nb_games} games!"