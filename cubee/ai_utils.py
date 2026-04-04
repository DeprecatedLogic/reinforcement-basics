from cubee.controller import GameController
from cubee.engine import GameEngine
from cubee.model import GameModel, Board
from cubee.player import Player, AI
from cubee.qtable_dao import QTableDAO
from cubee.qtable import QTable, SHARED_QTABLE
import logging
logger = logging.getLogger(__name__)

def training(*ais, epochs: int, episodes: int, efficiency_level: int = 0):
    """
    Train the AIs during `epochs * episodes` games.

    Args:
        epochs (int): Number of game batches.
        episodes (int): Number of games.
        efficieny_level (int): Usually used for increased performance in AI training.  
                0: Default  
                1: No game board output  
                2: No player turn message  
                3: No leaderboard output when the game's over

    Note:
        Epsilon decreases with each epoch.
    """

    logger.debug(f"=== Training AIs on {epochs} epochs and {episodes} episodes ===")
    for ai in ais:
        if type(ai) == AI: ai.training = True

    continue_training = []
    game_board = Board(5, 5)
    game_model = GameModel(game_board, *ais)
    game_engine = GameEngine(game_model)
    training_game = GameController(game_engine)
    logger.debug("Game controller created")
    logger.info("Starting AI training")
    for epoch in range(epochs):
        logger.debug(f"Epoch {epoch}")
        for episode in range(episodes):
            training_game.run(efficiency_level)
            training_game.restart_game(efficiency_level)

        QTableDAO.save(SHARED_QTABLE, f"cubee/QTables/qtable_epoch_{epoch}.pkl")
        
        for ai in ais:
            if type(ai) == AI:
                ai.next_epsilon()
                if ai.epsilon == 0.05 and ai not in continue_training:
                    logger.info(f"{ai.name} (AI) epsilon is {ai.epsilon}, less than 0.05")
                    user_input = input(f"{ai.name} (AI) epsilon reached the minimum value {ai.epsilon}, would you like to stop the training ? (y/n) ")
                    if user_input.strip().lower() in ('y', "yes"):
                        logger.debug(f"Training stopped by user (input={user_input})")
                        ai.training = False
                        return
                    continue_training.append(ai)
                print(f"{ai.name} (AI) epsilon is: {ai.epsilon}")

    ai.training = False
    logger.info("=== Training completed successfully ===")
    