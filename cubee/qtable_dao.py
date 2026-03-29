import pickle
from cubee.qtable import QTable

class QTableDAO:

    def save(self, qtable: QTable, file_path: str) -> None:
        with open(file_path, "wb") as f:
            pickle.dump(qtable.storage, f)

    def load(self, file_path: str) -> QTable:
        with open(file_path, "rb") as f:
            data = pickle.load(f)
        return QTable(preloaded_table=data)