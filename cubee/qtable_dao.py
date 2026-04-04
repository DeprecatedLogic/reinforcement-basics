import pickle
from cubee.qtable import QTable
import logging
logger = logging.getLogger(__name__)

class QTableDAO:

    @staticmethod
    def save(qtable: QTable, file_path: str) -> None:
        logger.debug(f"Saving the Q-table at path: {file_path}")
        with open(file_path, "wb") as f:
            pickle.dump(qtable.storage, f)
            logger.info("Q-table saved successfully")

    @staticmethod
    def load(file_path: str) -> QTable:
        logger.debug(f"Loading the Q-table at path: {file_path}")
        data = None
        with open(file_path, "rb") as f:
            data = pickle.load(f)
            logger.info("Q-table loaded successfully")
        return QTable(preloaded_table=data)
        