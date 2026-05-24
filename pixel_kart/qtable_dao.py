import os
import pickle
from pixel_kart.qtable import QTable
import logging
logger = logging.getLogger(__name__)

class QTableDAO:
    """
    Data Access Object managing persistence serialization loops for QTable structures.

    Handles high-level binary file input/output streams to store or restore model states 
    independently from execution lifecycle variables.
    """

    @staticmethod
    def save(qtable: QTable, file_path: str) -> None:
        """
        Serialize and commit a QTable internal storage map to persistent file systems.

        Note:
            Automatically generates missing parent directories along the path structure 
            to shield file writers from OS layout constraints.

        Args:
            qtable (QTable): The target data abstraction component to store.
            file_path (str): File destination path location tracking the output file.
        """
        logger.debug(f"Saving the Q-table at path: {file_path}")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            pickle.dump(qtable.storage, f)
            logger.info("Q-table saved successfully")

    @staticmethod
    def load(file_path: str) -> QTable:
        """
        Read and instantiate a structured utility model layer from disk storage.

        Args:
            file_path (str): Targeted binary storage file holding the serialized mapping structure.

        Returns:
            QTable: A newly configured instance wrapping the loaded memory structures.
        """
        logger.debug(f"Loading the Q-table at path: {file_path}")
        data = None
        with open(file_path, "rb") as f:
            data = pickle.load(f)
            logger.info("Q-table loaded successfully")
        return QTable(preloaded_table=data)
