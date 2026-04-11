import os

FILE_PATH = os.path.join(os.path.dirname(__file__), "circuits.txt")

def get_all():
    """Retrieve all circuits from the file as a dictionary {name: str}."""
    circuits = {}
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r", encoding="utf-8") as file:
            for line in file:
                if ":" in line:
                    name, circuit = line.split(":", 1)
                    if name.strip():
                        circuits[name.strip()] = circuit.strip()
    return circuits

def get_by_name(name):
    """Retrieve a circuit by its name."""
    circuits = get_all()
    return circuits.get(name)

def save_circuit(name, string):
    if not name:
        raise ValueError("Circuit name cannot be empty.")
    circuits = get_all()
    if name in circuits:
        raise ValueError(f"The circuit '{name}' already exists.")
    with open(FILE_PATH, "a", encoding="utf-8") as file:
        file.write(f"\n{name}:{string}")

def delete_circuit(name):
    if not name:
        raise ValueError("Circuit name cannot be empty.")
    circuits = get_all()
    if name not in circuits:
        raise ValueError(f"The circuit '{name}' does not exist.")
    del circuits[name]
    with open(FILE_PATH, "w", encoding="utf-8") as file:
        for circuit_name, circuit_data in circuits.items():
            file.write(f"{circuit_name}:{circuit_data}\n")

def update_circuit(name, string):
    circuits = get_all()
    if name not in circuits:
        raise ValueError(f"The circuit '{name}' does not exist.")
    circuits[name] = string
    with open(FILE_PATH, "w", encoding="utf-8") as file:
        for circuit_name, circuit_data in circuits.items():
            file.write(f"{circuit_name}:{circuit_data}\n")