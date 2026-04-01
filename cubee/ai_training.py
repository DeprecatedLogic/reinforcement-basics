from cubee.controller import GameController
from cubee.engine import GameEngine
from cubee.model import GameModel, Board
from cubee.player import Player
from cubee.ai import AI
from cubee.qtable_dao import QTableDAO
from cubee.qtable import QTable, SHARED_QTABLE
import logging
logger = logging.getLogger(__name__)

def training(*ais, epochs, episodes):
    # Train the AIs @ai1 and @ai2 during @nb_games games
    # epsilon decrease every @nb_epsilon games
    game_board = Board(5, 5)
    game_model = GameModel(game_board, *ais)
    game_engine = GameEngine(game_model)
    training_game = GameController(game_engine)
    logger.debug("Game controller created")
    logger.info("Starting AI training")
    for epoch in range(epochs):

        for episode in range(episodes):
            training_game.run()
            training_game.restart_game()

        for ai in ais:
            if type(ai)==AI : ai.next_epsilon()

        QTableDAO.save(SHARED_QTABLE, f"cubee/Qtables/qtable_epoch_{epoch}.pkl")