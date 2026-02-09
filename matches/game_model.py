from random import randint
from matches.player import Player

class GameModel():
    def __init__(self, nb: int, player1 : Player, player2 : Player, displayable: bool = True):
        self.nb = nb
        self.original_nb = nb
        self.displayable = displayable
        self.players = [player1, player2]

        player1.game = self
        player2.game = self

        self.current_player = None
        self.shuffle()

    def display(self, player_name: str):
        if self.displayable:
            print(f"Remaining matches: {self.nb}")
            print(f"It is {player_name}'s turn.")

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
    
    def get_remaining_matches(self) -> int:
        return self.nb
    
    def play(self):
        while not self.is_game_over():
            current_player = self.get_current_player()
            self.display(current_player.name)
            
            action = current_player.play()
            action = min(action, self.nb)
            
            self.step(action)
            
            if self.is_game_over():
                break
            
            self.switch_player()
        
        winner = self.get_winner()
        loser = self.get_loser()
        if winner and loser:
            winner.win()
            loser.lose()