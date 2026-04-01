import pickle
from cubee.qtable import QTable
import logging
logger = logging.getLogger(__name__)

class QTableDAO:

    @staticmethod
    def save(qtable: QTable, file_path: str) -> None:
        with open(file_path, "wb") as f:
            pickle.dump(qtable.storage, f)

    @staticmethod
    def load(file_path: str) -> QTable:
        data = None
        with open(file_path, "rb") as f:
            data = pickle.load(f)
        return QTable(preloaded_table=data)