from matches.player import Player as MatchesPlayer, Human as MatchesHuman, AI as MatchesAI
from matches.game_controller import GameController
from matches.game_model import GameModel
from cubee.colors import Color
from cubee.player import Human as CubeeHuman, Player as CubeePlayer, AI as CubeeAI
from cubee import ai_utils as cubee_ai_utils
from cubee.qtable_dao import QTableDAO
from main_gui import MainView
import tkinter as tk
from matches.ai_utils import training, compare_ai
import logging
import argparse
import sys

def parse_args():
    parser = argparse.ArgumentParser(
        description="Reinforcement Basics: train AI, load Q-tables, and start GUI",
        epilog=(
            "Examples:\n"
            "  # Train AI for 100 epochs with 5000 games per epoch\n"
            "  python main.py --train --epochs 100 --eps 5000\n\n"
            "  # Load a specific Q-table and start GUI\n"
            "  python main.py --load-qtable --qtable-path cubee/QTables/mytable.pkl\n\n"
            "  # Run without GUI (CLI only) and default training\n"
            "  python main.py --train --no-gui"
        ),
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "-l", "--log",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set logging level (default: %(default)s)"
    )

    parser.add_argument(
        "--epochs",
        type=int,
        default=None,
        help="Number of epochs for AI training (default: 50 if training enabled)"
    )
    parser.add_argument(
        "--eps", "--episodes",
        dest="episodes",
        type=int,
        default=None,
        help="Number of games per epoch (default: 10000 if training enabled)"
    )

    parser.add_argument(
        "--no-gui",
        action="store_true",
        help="Disable GUI mode"
    )
    parser.add_argument(
        "--train",
        action="store_true",
        help="Enable AI training"
    )
    parser.add_argument(
        "--load-qtable",
        action="store_true",
        help="Load Q-table from file"
    )

    parser.add_argument(
        "--qtable-path",
        type=str,
        default=None,
        help="Path to Q-table file (default: cubee/QTables/qtable_epoch_41.pkl)"
    )

    return parser.parse_args()


def setup_logging(level_str: str):
    level = getattr(logging, level_str.upper(), logging.INFO)

    logging.basicConfig(
        filename=".log",
        filemode="w",
        level=level,
        format="%(asctime)s [%(levelname)s] (%(filename)s:%(funcName)s:%(lineno)d) %(message)s"
    )

    return logging.getLogger(__name__)


if __name__ == "__main__":
    args = parse_args()
    logger = setup_logging(args.log)

    players = {
        "matches": {
            "Player 1": MatchesHuman("Player 1"),
            "Player 2": MatchesHuman("Player 2"),
            "Random": MatchesPlayer("Random"),
            "Alice": MatchesAI("Alice"),
            "Bobby": MatchesAI("Bobby"),
            "Randy": MatchesAI("Randy")
        },
        "cubee": {
            "Player 1": CubeeHuman("Player 1", Color.RED),
            "Player 2": CubeeHuman("Player 2", Color.BLUE),
            "AI 1": CubeeAI("AI 1", Color.GREEN, lr=0.1),
            "AI 2": CubeeAI("AI 2", Color.PURPLE, lr=0.1)
        },
        "pixelkart": {
            # TODO: Define PixelKart players here.
        }
    }

    gui_mode = not args.no_gui
    train_ai = args.train
    load_qtable = args.load_qtable

    if train_ai:
        cubee_ai1 = players["cubee"]["AI 1"]
        cubee_ai2 = players["cubee"]["AI 2"]

        epochs = args.epochs if args.epochs is not None else 50
        episodes = args.episodes if args.episodes is not None else 10000
        efficiency_level = 3

        logger.info(f"Training AI: epochs={epochs}, episodes={episodes}")

        cubee_ai1.epsilon = 0.10
        cubee_ai2.epsilon = 0.20
        cubee_ai_utils.training(
            cubee_ai1,
            cubee_ai2,
            epochs=epochs,
            episodes=episodes,
            efficiency_level=efficiency_level
        )

    if load_qtable:
        qtable_path = args.qtable_path or "cubee/QTables/qtable_epoch_41.pkl"

        logger.info(f"Loading Q-table from {qtable_path}")
        qtable = QTableDAO.load(qtable_path)

        if not qtable or len(qtable.storage) == 0:
            logger.critical(f"Failed to load Q-table: {qtable_path}")
            print("ERROR loading Q-table")
            sys.exit(1)

        print("===== Q-Table =====")
        print(qtable)
        print("===================")

    if gui_mode:
        logger.info("Starting GUI")
        root = tk.Tk()
        app = MainView(root, players=players)
        root.mainloop()