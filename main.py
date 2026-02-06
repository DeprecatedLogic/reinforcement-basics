from matches.player import Player, Human
from matches.game_controller import GameController

if __name__ == "__main__":
    p1 = Player("AI")
    p2 = Human("Player2")

    app = GameController(p1, p2, nb_matches=21)