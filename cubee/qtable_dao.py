import os
import pickle
from cubee.qtable import QTable
import logging
logger = logging.getLogger(__name__)

class QTableDAO:

    @staticmethod
    def save(qtable: QTable, file_path: str) -> None:
        """
        Persist a Q-table to disk using pickle serialization.

        The underlying storage dictionary of the QTable is written to the specified
        file path.
        
        Note:
            Parent directories are created if they do not exist.

        Args:
            qtable (QTable): The QTable instance to save.
            file_path (str): Destination file path for the serialized Q-table.
        """
        logger.debug(f"Saving the Q-table at path: {file_path}")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            pickle.dump(qtable.storage, f)
            logger.info("Q-table saved successfully")

    @staticmethod
    def load(file_path: str) -> QTable:
        """
        Load a Q-table from disk.

        The file is deserialized using pickle and used to initialize a QTable
        instance with preloaded state-action values.

        Args:
            file_path (str): Path to the serialized Q-table file.

        Returns:
            QTable: A QTable instance initialized with the loaded data.
        """
        logger.debug(f"Loading the Q-table at path: {file_path}")
        data = None
        with open(file_path, "rb") as f:
            data = pickle.load(f)
            logger.info("Q-table loaded successfully")
        return QTable(preloaded_table=data)
        