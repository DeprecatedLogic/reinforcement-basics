# === Matches (Nim21) ===
from matches.player import Player as MatchesPlayer, Human as MatchesHuman, AI as MatchesAI
from matches.ai_utils import training, compare_ai
# === Cubee ===
from cubee.colors import Color as CubeeColor
from cubee.player import Human as CubeeHuman, Player as CubeePlayer, AI as CubeeAI
from cubee import ai_utils as cubee_ai_utils
from cubee.qtable_dao import QTableDAO
# === Pixel Kart ===
from pixel_kart.colors import Color as PixelKartColor
from pixel_kart.player import Human as PixelKartHuman, Player as PixelKartPlayer, AI as PixelKartAI
# === Other modules ===
from main_gui import MainView
import tkinter as tk
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
        default=50,
        help="Number of epochs for AI training (default: 50 if training enabled)"
    )
    parser.add_argument(
        "--eps", "--episodes",
        dest="episodes",
        type=int,
        default=10000,
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
        help="Path to Q-table file (e.g.: cubee/QTables/qtable_epoch_50.pkl)"
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
            "Player 1": CubeeHuman("Player 1", CubeeColor.RED),
            "Player 2": CubeeHuman("Player 2", CubeeColor.BLUE),
            "AI 1": CubeeAI("AI 1", CubeeColor.GREEN, lr=0.1),
            "AI 2": CubeeAI("AI 2", CubeeColor.PURPLE, lr=0.1)
        },
        "pixel_kart": {
            "Human": PixelKartHuman("Human", PixelKartColor.BLUE),
            "Random AI": PixelKartPlayer("Random AI", PixelKartColor.RED)
        }
    }
    
    # TODO: Use parsed args to decide the events

    logger.info("Starting GUI")
    root = tk.Tk()
    app = MainView(root, players=players)
    root.mainloop()