from random import randint
from matches.player import Player

class GameModel():
    def __init__(self, nb: int, player1 : Player, player2 : Player):
        self.nb = nb
        self.original_nb = nb
        self.players = [player1, player2]

        player1.game = self
        player2.game = self

        self.current_player = None
        self.shuffle()

    def step(self, action: int):
        if action < 1 or action > 3 or action > self.nb:
            raise ValueError("Action invalide")
        self.nb -= action

    def shuffle(self):
        self.current_player = self.players[randint(0, 1)]

    def reset(self):
        self.nb = self.original_nb
        self.shuffle()

    def switch_player(self):
        if self.current_player == self.players[0]:
            self.current_player = self.players[1]
        else:
            self.current_player = self.players[0]

    def is_game_over(self):
        return self.nb <= 0

    def get_current_player(self):
        return self.current_player

    def get_winner(self):
        if not self.is_game_over():
            return None
        return self.players[0] if self.current_player == self.players[1] else self.players[1]

    def get_loser(self):
        if not self.is_game_over():
            return None
        return self.current_player