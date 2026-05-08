from pixel_kart.controller import GameController
from pixel_kart.engine import GameEngine
from pixel_kart.model import GameModel, Board
from pixel_kart import dao as CircuitDAO
from pixel_kart.player import Player, AI
from pixel_kart.qtable_dao import QTableDAO
from pixel_kart.qtable import QTable, SHARED_QTABLE
import logging
logger = logging.getLogger(__name__)

def set_mode(*ais, training_mode: bool):
    """_summary_

    Args:
        *ais: _description_
        training_mode (bool): _description_
    """
    logger.info(f"Setting AIs in {'training' if training_mode else 'inference'} mode")
    for ai in ais:
        if isinstance(ai, AI): ai.training = False

def training(*ais, epochs: int, episodes: int, laps: int = 1, efficiency_level: int = 0, unattended: bool = False) -> None:
    """
    Train the AIs during `epochs * episodes` games.

    Note:
        Epsilon decreases with each epoch.  
        AIs are automatically set in training mode while training,
        and in inference mode at the end.

    Args:
        epochs (int): Number of game batches.
        episodes (int): Number of games.
        efficiency_level (int): Usually used for increased performance in AI training.  
                0: Default  
                1: No game board output  
                2: No player turn message  
                3: No leaderboard output when the game's over
    """

    logger.debug(f"=== Training AIs on {epochs} epochs and {episodes} episodes ===")
    set_mode(*ais, training_mode=True)

    continue_training = []
    grid = CircuitDAO.get_by_name("Basic")
    board = Board.load(grid)
    logger.debug("Board is ready")
    model = GameModel(board, *ais, laps_required=laps)
    logger.debug("Game model is ready")
    engine = GameEngine(model)
    logger.debug("Game engine is ready")
    training_game = GameController(engine)
    logger.debug("Game controller is ready")

    logger.info("Starting AI training")
    for epoch in range(epochs):
        logger.info(f"Epoch {epoch}")
        print(f"=== Epoch {epoch} ===")
        for episode in range(episodes):
            # Resets game state and runs the game automatically
            training_game.restart_game(efficiency_level)

        # Q-Table checkpoint
        QTableDAO.save(SHARED_QTABLE, f"pixel_kart/QTables/qtable_epoch_{epoch}.pkl")
        
        for ai in ais:
            if isinstance(ai, AI):
                ai.next_epsilon()

                if ai.epsilon == 0.05 and ai not in continue_training:
                    logger.info(f"{ai.name} (AI) epsilon reached the minimum value {ai.epsilon}")

                    if unattended:
                        # Skip the prompt and keep going
                        logger.info("Unattended mode active. Continuing training automatically")
                        continue_training.append(ai)
                    else:
                        # Wait for human interaction
                        user_input = input(f"{ai.name} epsilon hit minimum. Stop training? (y/n) ")
                        if user_input.strip().lower() in ('y', "yes"):
                            logger.debug(f"Training stopped by user (input={user_input})")
                            set_mode(*ais, training_mode=False)
                            return # exit the training loop early
                        continue_training.append(ai)

                print(f"{ai.name} (AI) epsilon is: {ai.epsilon}")

    set_mode(*ais, training_mode=False)
    logger.info("=== Training completed successfully ===")
    