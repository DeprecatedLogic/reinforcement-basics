from matches.player import Player, Human, AI
from matches.game_controller import GameController
from matches.game_model import GameModel
from cubee.colors import Color
from cubee.player import Human as CubeeHuman, Player as CubeePlayer
from main_gui import MainView
import tkinter as tk
from matches.ai_utils import training, compare_ai

if __name__ == "__main__":
    players = {
        "matches": {
            "Player 1": Human("Player 1"),
            "Player 2": Human("Player 2"),
            "Random": Player("Random"),
            "Alice": AI("Alice"),
            "Bobby": AI("Bobby"),
            "Randy": AI("Randy")
        },
        "cubee": {
            "Player 1": CubeeHuman("Player 1", Color.RED),
            "Player 2": CubeeHuman("Player 2", Color.BLUE)
        },
        "pixelkart": {
            # TODO: Define PixelKart players here.
        }
    }

    #bobby = players["matches"]["Bobby"]
    #alice = players["matches"]["Alice"]

    #training(bobby, alice, 100000, 10, 21)
    #compare_ai(bobby, alice)

    # bobby.download("bobby_params")
    #bobby.load("bobby_params.json")

    root = tk.Tk()
    app = MainView(root, players=players)
    root.mainloop()