from cubee.colors import Color
from cubee.player import Human as CubeeHuman, Player as CubeePlayer
from cubee.ai import AI as CubeeAI
from cubee. cells import Cell
from cubee.controller import GameController
from cubee.qtable_dao import QTableDAO
from cubee.qtable import SHARED_QTABLE
from cubee.ai_training import training as cubeetraining

#MATCHES
from matches.player import Player, Human, AI
from matches.game_controller import GameController
from matches.game_model import GameModel
from matches.ai_utils import training, compare_ai

#TKINTER
from main_gui import MainView
import tkinter as tk

#LOGGING
import logging
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reinforcement Basics")
    parser.add_argument(
        "-l", "--log",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set logging level"
    )
    args = parser.parse_args()

    log_level = getattr(logging, args.log.upper(), logging.INFO)

    logging.basicConfig(
        filename=".log",
        filemode="w",
        level=log_level,
        format="%(asctime)s [%(levelname)s] (%(filename)s:%(funcName)s:%(lineno)d) %(message)s"
    )

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
            "Player 2": CubeeHuman("Player 2", Color.BLUE),
            "Ai1": CubeeAI("Ai1", Color.GREEN),
            "Ai2": CubeeAI("Ai2", Color.ORANGE)
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

    ai1 = players["cubee"]["Ai1"]
    ai1.epsilon = 0
    ai2 = players["cubee"]["Ai2"]

    #cubeetraining(ai1, ai2, epochs=50, episodes=10000)
    
    
    SHARED_QTABLE = QTableDAO.load("cubee/Qtables/qtable_epoch_52.pkl")
    if len(SHARED_QTABLE.storage) == 0:
        print("ERROR loading file")
        exit(1)

    print(SHARED_QTABLE.storage)

    root = tk.Tk()
    app = MainView(root, players=players)
    root.mainloop()
    
