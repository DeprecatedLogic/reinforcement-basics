import os
import pickle
from pixel_kart.cells import LEGACY_LABEL_TO_CELL, Cell
import logging
logger = logging.getLogger(__name__)

FILE_PATH = os.path.join(os.path.dirname(__file__), "circuits.pkl")

def get_all() -> dict:
    """
    Retrieve all circuits from the pickle file.
    
    Returns:
        dict: A dictionary mapping circuit names to their 2D grid of Cell Enums.
              Format: { "Circuit 1": [[Cell.ROAD, Cell.WALL...], ...], ... }
    """
    if not os.path.exists(FILE_PATH):
        logger.debug(f"No circuit file found at {FILE_PATH}. Returning empty dict.")
        return {}
        
    try:
        with open(FILE_PATH, "rb") as file:
            circuits = pickle.load(file)
            return circuits
    except (EOFError, pickle.UnpicklingError) as e:
        logger.error(f"Failed to load circuits from {FILE_PATH}: {e}")
        return {}

def get_by_name(name: str) -> list | None:
    """Retrieve a specific circuit grid by its name."""
    circuits = get_all()
    return circuits.get(name)

def save_circuit(name: str, grid: list) -> None:
    """
    Save a new circuit to the pickle file.
    
    Args:
        name (str): The name of the circuit.
        grid (list[list[Cell]]): The 2D array of Cell Enums.
    """
    if not name or not name.strip():
        raise ValueError("Circuit name cannot be empty.")
        
    circuits = get_all()
    
    if name in circuits:
        raise ValueError(f"The circuit '{name}' already exists.")
        
    circuits[name] = grid
    _write_to_file(circuits)
    logger.info(f"Successfully saved circuit: '{name}'")

def update_circuit(name: str, grid: list) -> None:
    """
    Overwrite an existing circuit with a new grid.
    
    Args:
        name (str): _description_
        grid (list): _description_
    """
    if not name:
        raise ValueError("Circuit name cannot be empty.")
        
    circuits = get_all()
    
    if name not in circuits:
        raise ValueError(f"The circuit '{name}' does not exist.")
        
    circuits[name] = grid
    _write_to_file(circuits)
    logger.info(f"Successfully updated circuit: '{name}'")

def delete_circuit(name: str) -> None:
    """
    Delete a circuit from the pickle file.

    Args:
        name (str): _description_

    Raises:
        ValueError: _description_
        ValueError: _description_
    """
    if not name:
        raise ValueError("Circuit name cannot be empty.")
        
    circuits = get_all()
    
    if name not in circuits:
        raise ValueError(f"The circuit '{name}' does not exist.")
        
    del circuits[name]
    _write_to_file(circuits)
    logger.info(f"Successfully deleted circuit: '{name}'")

def _write_to_file(circuits: dict) -> None:
    """Helper method to handle the actual pickling process."""
    with open(FILE_PATH, "wb") as file:
        pickle.dump(circuits, file)

def import_legacy_txt(txt_file_path: str = os.path.join(os.path.dirname(__file__), "circuits.txt")) -> None:
    """
    Reads a legacy circuits.txt file, converts the circuits to the new Cell enum grid format,
    and saves them to the pickle database.

    Args:
        txt_file_path (str, optional): _description_. Defaults to os.path.join(os.path.dirname(__file__), "circuits.txt").
    """
    if not os.path.exists(txt_file_path):
        logger.warning(f"Legacy file {txt_file_path} not found.")
        return

    circuits = get_all()
    imported_count = 0

    special_bitmask = Cell.START_LINE | Cell.FINISH_LINE | Cell.CHECKPOINT

    with open(txt_file_path, "r", encoding="utf-8") as file:
        for line in file:
            if ":" in line:
                name, circuit_data = line.split(":", 1)
                name = name.strip()
                circuit_data = circuit_data.strip()
                
                # Skip empty lines or circuits that have already been imported/created
                if not name or not circuit_data or name in circuits:
                    continue
                    
                grid = []
                for row_str in circuit_data.split(","):
                    # Map the letter to the Cell Enum, defaulting to GRASS if the letter is unknown
                    grid_row = []
                    for char in row_str:
                        cell = LEGACY_LABEL_TO_CELL.get(char.upper(), Cell.GRASS)
                        if cell & special_bitmask: # check for the start/finish line and place something under it
                            cell |= Cell.ROAD
                        grid_row.append(cell)
                    grid.append(grid_row)
                
                circuits[name] = grid
                imported_count += 1
                
    if imported_count > 0:
        _write_to_file(circuits)
        logger.info(f"Successfully imported {imported_count} legacy circuits.")
