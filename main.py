# === Matches (Nim21) ===
from matches.player import Player as MatchesPlayer, Human as MatchesHuman, AI as MatchesAI
from matches.ai_utils import training, compare_ai

# === Cubee ===
from cubee.colors import Color as CubeeColor
from cubee.player import Human as CubeeHuman, Player as CubeePlayer, AI as CubeeAI
from cubee.model import GameModel as CubeeModel, Board as CubeeBoard
from cubee.engine import GameEngine as CubeeEngine
from cubee.controller import GameController as CubeeController
from cubee import ai_utils as cubee_ai_utils
from cubee.qtable_dao import QTableDAO

# === Pixel Kart ===
from pixel_kart.colors import Color as PixelKartColor
from pixel_kart.player import Human as PixelKartHuman, Player as PixelKartPlayer, AI as PixelKartAI
from pixel_kart import ai_utils as pk_ai_utils, circuit_dao as CircuitDAO
from pixel_kart.qtable_dao import QTableDAO as PKQTableDAO
from pixel_kart.qtable import SHARED_QTABLE as PK_SHARED_QTABLE
from pixel_kart.engine import GameEngine as PKEngine
from pixel_kart.model import GameModel as PKModel, Board as PKBoard
from pixel_kart.controller import GameController as PKController

# === Other modules ===
from main_gui import MainView
import tkinter as tk
import logging
import argparse
import sys

def parse_args():
    """
    Parse command-line arguments for configuring the game environment launcher.

    Returns:
        argparse.Namespace: Parsed arguments detailing execution modes, specific game settings,  
            and AI reinforcement learning hyperparameters.
    """

    parser = argparse.ArgumentParser(
        description=(
            "AI Project - Reinforcement Learning in Game Environments.\n"
            "Play, simulate, or train Q-Learning agents across three distinct environments: \n"
            "Matches, Cubee, and Pixel Kart. Supports interactive GUI gameplay, headless \n"
            "CLI simulation, and high-efficiency training pipelines.\n\n"
            "===============================================================================\n"
            "     COMMON WORKFLOWS & EXAMPLES (Copy & Paste these to test the project)\n"
            "===============================================================================\n\n"
            "  1. Play Normally\n"
            "     Open the GUI with all 3 games available:\n"
            "     $ python main.py\n\n"
            "  2. See Available Tracks for Pixel Kart\n"
            "     List all circuits currently saved in the database:\n"
            "     $ python main.py --show-circuits\n\n"
            "  3. Fast AI Training Check (Proof of Concept)\n"
            "     Run a very short training loop to verify the Bellman math works:\n"
            "     $ python main.py --game pixelkart --train --epochs 5 --eps 100 --efficiency 1\n\n"
            "  4. Deep AI Training (Overnight / Headless)\n"
            "     Train a smart agent at maximum speed without GUI or prompts:\n"
            "     $ python main.py --game pixelkart --train --epochs 50 --eps 200000 --parallel --efficiency 3 --unattended --no-launch -l WARNING\n\n"
            "  5. Watch a Trained AI Drive\n"
            "     Load a saved brain and open the GUI to watch it race:\n"
            "     $ python main.py --game pixelkart --qtable-path pixel_kart/QTables/qtable_epoch_99.pkl\n\n"
            "  6. Headless Race (Not Recommended)\n"
            "     Run a 3-lap text-only race on the 'Large' track:\n"
            "     $ python main.py --game pixelkart --circuit Large --laps 3 --no-gui\n\n"
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
        help="Number of epochs for AI training (default: %(default)s; affects training)"
    )
    parser.add_argument(
        "--eps", "--episodes",
        dest="episodes",
        type=int,
        default=10000,
        help="Number of games per epoch (default: %(default)s; affects training)"
    )
    parser.add_argument(
        "--lr", "--learning-rate",
        dest="learning_rate",
        type=float,
        default=0.01,
        help="How much the AI learns from a lesson (default: %(default)s; affects training)"
    )
    parser.add_argument(
        "--epsilon",
        type=float,
        default=1.0,
        help="How smart AI should be; 0 for smartest, 1 for random (default: %(default)s; affects game & training)"
    )
    parser.add_argument(
        "--gamma",
        type=float,
        default=0.95,
        help="Controls how far and how strongly rewards propagate backward through time (default: %(default)s; affects training)"
    )
    parser.add_argument(
        "--epsilon-coefficient",
        type=float,
        default=0.95,
        help="Controls how fast the epsilon decays, higher is slower (default: %(default)s; affects training)"
    )
    parser.add_argument(
        "--min-epsilon",
        type=float,
        default=0.05,
        help="The minimum value epsilon can reach while in training (default: %(default)s)"
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Enable multiprocessing for faster AI training (WARNING: uses A LOT more memory)"
    )
    parser.add_argument(
        "--efficiency",
        type=int,
        default=0,
        choices=[0, 1, 2, 3],
        help="Avoid terminal output, level 3 has no output (default: %(default)s; affects game & training)"
    )
    parser.add_argument(
        "--opp", "--opponent",
        dest="opponent",
        default="AI",
        choices=["AI", "random"],
        help="Set the opponent with whom the AI will play against (default: %(default)s; affects training)"
    )

    parser.add_argument(
        "--game",
        default="cubee",
        choices=["matches", "cubee", "pixelkart"],
        help="The desired game out of the three (default: %(default)s; affects CLI, Q-Table, and training)"
    )
    parser.add_argument(
        "--no-launch",
        action="store_true",
        help="Do not launch the game loop after initialization/training"
    )
    parser.add_argument(
        "--no-gui",
        action="store_true",
        help="Disable GUI mode (launches in CLI mode)"
    )
    parser.add_argument(
        "--circuit",
        type=str,
        default="Basic",
        help="The circuit's name to load (default: %(default)s; affects CLI)"
    )
    parser.add_argument(
        "--show-circuits",
        action="store_true",
        help="Show a list of circuit names available and exit"
    )
    parser.add_argument(
        "--laps",
        type=int,
        default=1,
        help="Number of laps required to win (default: %(default)s; affects CLI and training)"
    )
    parser.add_argument(
        "--train",
        action="store_true",
        help="Enable AI training"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Enable AI evaluation/testing mode"
    )
    parser.add_argument(
        "--test-matches",
        type=int,
        default=500,
        help="Number of matches to play during testing mode (default: %(default)s)"
    )
    parser.add_argument(
        "--skip-checkpoints",
        action="store_true",
        help="Do not create a checkpoint for every epoch"
    )
    parser.add_argument(
        "--unattended",
        action="store_true",
        help="Run AI training without asking for confirmation when epsilon decays"
    )

    parser.add_argument(
        "--qtable-path",
        type=str,
        nargs="+",
        default=None,
        help="Path(s) to Q-table file(s) (accepts 1 or 2 paths, e.g.: cubee/QTables/qtable_epoch_50.pkl cubee/QTables/qtable_epoch_99.pkl)"
    )
    parser.add_argument(
        "--share-qtable",
        action="store_true",
        help="Share a single Q-table instance between AI 1 and AI 2"
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

    # === Circuit Listing ===
    if args.show_circuits:
        circuits = CircuitDAO.get_all()
        print("Circuits available:")
        for name in circuits.keys():
            print(f"    {name}")
        sys.exit(0)

    # === Player Dictionary ===
    players = {
        "matches": {
            "Player 1": MatchesHuman("Player 1"),
            "Player 2": MatchesHuman("Player 2"),
            "Random AI": MatchesPlayer("Random AI"),
            "Alice": MatchesAI("Alice", epsilon=args.epsilon, lr=args.learning_rate, gamma=args.gamma),
            "Bobby": MatchesAI("Bobby", epsilon=args.epsilon, lr=args.learning_rate, gamma=args.gamma),
            "Randy": MatchesAI("Randy", epsilon=args.epsilon, lr=args.learning_rate, gamma=args.gamma)
        },
        "cubee": {
            "Player 1": CubeeHuman("Player 1", CubeeColor.RED),
            "Player 2": CubeeHuman("Player 2", CubeeColor.BLUE),
            "Random AI": CubeePlayer("Random AI", CubeeColor.ORANGE),
            "AI 1": CubeeAI("AI 1", CubeeColor.GREEN, epsilon=args.epsilon, lr=args.learning_rate, gamma=args.gamma, training=False),
            "AI 2": CubeeAI("AI 2", CubeeColor.PURPLE, epsilon=args.epsilon, lr=args.learning_rate, gamma=args.gamma, training=False)
        },
        "pixel_kart": {
            "Player 1": PixelKartHuman("Player 1", PixelKartColor.BLUE),
            "Player 2": PixelKartHuman("Player 2", PixelKartColor.PURPLE),
            "Random AI": PixelKartPlayer("Random AI", PixelKartColor.RED),
            "AI 1": PixelKartAI("AI 1", PixelKartColor.ORANGE, epsilon=args.epsilon, lr=args.learning_rate, gamma=args.gamma, training=False),
            "AI 2": PixelKartAI("AI 2", PixelKartColor.PINK, epsilon=args.epsilon, lr=args.learning_rate, gamma=args.gamma, training=False),
        }
    }

    # === Load Pre-Trained Brains (Inference / Testing) ===
    if args.qtable_path:
        logger.info(f"Loading Q-Table(s) from {args.qtable_path} for game {args.game}")
        try:
            if args.game == "cubee":
                ai_keys = ["AI 1", "AI 2"]
                for idx, path in enumerate(args.qtable_path[:2]):
                    loaded_table = QTableDAO.load(path)
                    target_ai = players["cubee"][ai_keys[idx]]
                    target_ai.qtable = loaded_table
                    logger.info(f"Successfully loaded {len(loaded_table.storage)} states into {target_ai.name} memory from {path}")
            elif args.game == "pixelkart":
                loaded_table = PKQTableDAO.load(args.qtable_path[0])
                PK_SHARED_QTABLE.storage = loaded_table.storage
                logger.info(f"Successfully loaded {len(PK_SHARED_QTABLE.storage)} states into Pixel Kart memory")
            else:
                logger.info(f"Cannot load Q-Table for the game '{args.game}', skipping")
        except Exception as e:
            logger.error(f"Failed to load Q-Table: {e}")
            sys.exit(1)

    # === Share Q-Table if requested ===
    if args.share_qtable and args.game == "cubee":
        players["cubee"]["AI 2"].qtable = players["cubee"]["AI 1"].qtable
        logger.info("Shared Q-Table mode enabled: AI 2's qtable now points to AI 1's qtable")

    # === Run Testing ===
    if args.test:
        logger.info(f"Starting {args.game.upper()} AI Testing ({args.test_matches} matches)")
        if args.game == "cubee":
            # Auto-detect opponents based on number of provided qtable paths
            p1 = players["cubee"]["AI 1"]
            if args.qtable_path and len(args.qtable_path) >= 2:
                p2 = players["cubee"]["AI 2"]
            else:
                p2 = players["cubee"]["Random AI"] if args.opponent == "random" else players["cubee"]["AI 2"]

            cubee_ai_utils.test_ais(p1, p2, nb_matches=args.test_matches, efficiency_level=args.efficiency)
        else:
            print(f"Testing mode not implemented for {args.game}")

    # === Run Training ===
    if args.train:
        logger.info(f"Starting {args.game.upper()} AI Training: {args.epochs} epochs, {args.episodes} episodes")
        
        if args.game == "matches":
            # Epochs in this case are used as `nb_epsilon` because matches' architecture is old
            # and different from the rest of the games (it's used to decrease epsilon by doing: current_game_number % nb_epsilon)
            training(
                players["matches"]["Alice"],
                players["matches"]["Bobby"],
                nb_games=args.episodes,
                nb_epsilon=args.epochs,
                nb_matches=25
            )
        elif args.game == "cubee":
            cubee_ai_utils.training(
                players["cubee"]["AI 1"],
                players["cubee"]["AI 2"] if args.opponent == "AI" else players["cubee"]["Random AI"],
                epochs=args.epochs,
                episodes=args.episodes,
                epsilon=args.epsilon,
                efficiency_level=args.efficiency,
                unattended=args.unattended,
                parallel=args.parallel,
                epsilon_coefficient=args.epsilon_coefficient,
                min_epsilon=args.min_epsilon,
                gamma=args.gamma,
                learning_rate=args.learning_rate,
                opponent=args.opponent,
                skip_checkpoints=args.skip_checkpoints,
                epoch_summary=True,
                shared_qtable=args.share_qtable
            )
        elif args.game == "pixelkart":
            pk_ai_utils.training(
                players["pixel_kart"]["AI 1"],
                players["pixel_kart"]["AI 2"],
                epochs=args.epochs,
                episodes=args.episodes,
                epsilon=args.epsilon,
                laps=args.laps,
                circuit_name=args.circuit,
                efficiency_level=args.efficiency,
                unattended=args.unattended,
                parallel=args.parallel
            )

    # === Launch the App ===
    if not args.no_launch and not args.test:
        if args.no_gui:
            # Use efficiency 0 to get every output from the controller... otherwise it's unplayable
            # unless you can imagine the whole board and every move your opponent and you are making :P
            
            logger.info(f"Starting {args.game} in CLI mode")
            # A lot of default values are used
            # To avoid this, we should extend the arguments in the `parse_args` function... (future update?)
            if args.game == "pixelkart":
                grid = CircuitDAO.get_by_name(args.circuit)
                if not grid:
                    print(f"Error: Circuit '{args.circuit}' not found")
                    sys.exit(1)

                board = PKBoard.load(grid)
                model = PKModel(
                    board, 
                    players["pixel_kart"]["Player 1"],
                    players["pixel_kart"]["AI 1"],
                    laps_required=args.laps
                )
                engine = PKEngine(model)
                controller = PKController(engine)
                controller.run(efficiency_level=0)

            elif args.game == "cubee":
                board = CubeeBoard(5, 5)
                model = CubeeModel(
                    board, 
                    players["cubee"]["Human"], 
                    players["cubee"]["AI 1"],
                )
                engine = CubeeEngine(model)
                controller = CubeeController(engine)
                controller.run(efficiency_level=0)
            else:
                print(f"CLI mode not fully configured for {args.game} within main.py")
        else:
            logger.info("Starting GUI")
            root = tk.Tk()
            app = MainView(root, players=players)
            root.mainloop()
    else:
        logger.info("Skipping game launch (--no-launch passed). Process complete")
