import os
import pickle
from pixel_kart.cells import LEGACY_LABEL_TO_CELL, Cell
import logging
logger = logging.getLogger(__name__)

FILE_PATH = os.path.join(os.path.dirname(__file__), "circuits.pkl")

def get_all() -> dict:
    """
    Retrieve all circuits from the pickle database file.
    
    Note:
        If the database file does not exist, or if it is corrupt/empty, 
        this function catches the exception and safe-defaults to an empty dictionary.

    Returns:
        dict: A dictionary mapping circuit names (str) to their 2D grid matrix of Cell Enums.
              Format: { "Circuit Name": [[Cell.ROAD, Cell.WALL...], ...], ... }
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
    """
    Retrieve a specific circuit layout matrix by its unique name string.

    Args:
        name (str): The name identifier of the target circuit.

    Returns:
        list[list[Cell]] | None: A 2D matrix of Cell instances if found; 
                                 otherwise, returns None.
    """
    circuits = get_all()
    return circuits.get(name)

def save_circuit(name: str, grid: list) -> None:
    """
    Save a new circuit layout configuration to the pickle database file.
    
    Note:
        This function strictly guards against overwriting existing records. 
        Use `update_circuit` instead if modification of an existing circuit is required.

    Args:
        name (str): The unique descriptive name of the circuit.
        grid (list[list[Cell]]): The 2D matrix of Cell Enums representing the track layout.

    Raises:
        ValueError: If the name is blank, whitespace-only, or if a circuit 
                    with that name already exists in the database.
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
    Overwrite an existing circuit configuration in the pickle database file with a new grid.
    
    Args:
        name (str): The name identifier of the existing circuit to modify.
        grid (list[list[Cell]]): The updated 2D matrix of Cell Enums.

    Raises:
        ValueError: If the name is blank or if the circuit does not exist in the database.
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
    Remove an existing circuit configuration from the pickle database file.

    Args:
        name (str): The name identifier of the circuit to delete.

    Raises:
        ValueError: If the name is blank or if the target circuit does not exist.
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
    """
    Helper method to handle the physical serialization and disk writing process.

    Args:
        circuits (dict): The complete state mapping dictionary to serialize.
    """
    with open(FILE_PATH, "wb") as file:
        pickle.dump(circuits, file)

def import_legacy_txt(txt_file_path: str = os.path.join(os.path.dirname(__file__), "circuits.txt")) -> None:
    """
    Parse a legacy raw text map database, convert characters into bitmasked grid cells, 
    and append non-conflicting circuits into the modern pickle database.

    Note:
        In old plain-text track assets, specialized landmarks like lines or markers 
        replaced the physical track terrain entirely instead of overlaying it. To preserve 
        underlying physics and GUI constraints, any cell parsed matching `special_bitmask` 
        is structurally combined with `Cell.ROAD` via a bitwise OR operation.
        
        If a record parsed from the text document matches a key that already exists in 
        the master binary database, it skips compilation passively to prevent unintended overwrites.

    Args:
        txt_file_path (str, optional): System file path pointing to the source text file. 
                                       Defaults to a relative path pointing to "circuits.txt".
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
                if not name or not circuit_data:
                    logger.debug(f"Circuit name or circuit data is empty, skipping line.")
                    continue
                elif name in circuits:
                    logger.debug(f"Skipping legacy circuit '{name}': Already exists in database.")
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
