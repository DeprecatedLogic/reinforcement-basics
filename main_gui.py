# === Matches (Nim21) ===
from matches.game_controller import GameController
from matches.player import Human, Player
# === Cubee ===
from cubee.controller import GameController as CubeeController
from cubee.engine import GameEngine as CubeeEngine
from cubee.gui import GUI as CubeeGUI
from cubee.model import GameModel as CubeeModel, Board as CubeeBoard
from cubee.player import Player as CubeePlayer, Human as CubeeHuman
# === Pixel Kart ===
from pixel_kart.cells import Cell
from pixel_kart.controller import GameController as PixelKartController
from pixel_kart.engine import GameEngine as PixelKartEngine
from pixel_kart.model import GameModel as PixelKartModel, Board as PixelKartBoard
from pixel_kart.player import Player as PixelKartPlayer
from pixel_kart.gui import GUI as PixelKartGUI # TODO: [IMPORTANT] Implement the GUI class before running the main GUI!
from pixel_kart import dao
from pixel_kart.editor import CircuitEditor
# === Other Modules ===
import tkinter as tk
from tkinter import ttk, messagebox
import logging
logger = logging.getLogger(__name__)

class MainView(tk.Frame):
    def __init__(self, parent, players: dict[dict[Player]]):
        """
        Initialize the main GUI view.

        Args:
            parent: The parent Tkinter window.
            players: Dictionary of games to their available players (keyed by display name).
        """
        super().__init__(parent)
        self.parent = parent
        self.players = players
        self.current_game_frame = None
        self.init_ui()

    def init_ui(self):
        self.parent.title("Projet IA")
        self.parent.geometry("700x500")
        self.parent.resizable(False, False)
        self.parent.configure(bg="#2C3E50")  # Dark blue-gray background

        self.create_menu_frame()
        self.show_menu()

    def create_menu_frame(self):
        """Create the main menu frame with game buttons and settings."""
        self.menu_frame = tk.Frame(self.parent, padx=40, pady=40, bg="#2C3E50")

        title = tk.Label(self.menu_frame, text="Projet IA", font=("Arial", 28, "bold"), bg="#2C3E50", fg="#FFFFFF")
        title.pack(pady=(0, 40))

        games = [
            ("Allumettes", self.open_matches_settings),
            ("Cubee", self.open_cubee_settings),
            ("PixelKart", self.open_pixelkart_settings)
        ]

        for name, command in games:
            btn = tk.Button(self.menu_frame, text=name, font=("Helvetica", 16),
                            width=15, height=2, command=command,
                            bg="#3498DB", fg="#FFFFFF", activebackground="#2980B9", activeforeground="#FFFFFF")
            btn.pack(pady=15)

    def show_menu(self):
        """Display the menu frame and hide any active game frame."""
        if self.current_game_frame:
            self.current_game_frame.pack_forget()
        self.menu_frame.pack(expand=True)

    def hide_menu(self):
        """Hide the menu frame"""
        self.menu_frame.pack_forget()

    def start_allumettes(self, player1: Player, player2: Player):
        """
        Start the Matches (Allumettes) game with selected players.

        Args:
            player1: First player instance.
            player2: Second player instance.
        """
        self.hide_menu()

        game_frame = tk.Frame(self.parent, bg="#2C3E50")
        game_frame.pack(fill="both", expand=True)
        self.current_game_frame = game_frame

        GameController(player1, player2, nb_matches=21, parent=game_frame)

        self._add_back_button(game_frame)

    def start_cubee(self, player1: CubeePlayer, player2: CubeePlayer):
        """
        Start the Cubee game with selected players.

        Args:
            player1: First player instance.
            player2: Second player instance.
        """
        self.hide_menu()

        game_frame = tk.Frame(self.parent, bg="#2C3E50")
        game_frame.pack(fill="both", expand=True)
        self.current_game_frame = game_frame

        model = CubeeModel(
            CubeeBoard(rows = 5, columns = 5),
            player1,
            player2
        )

        gui = CubeeGUI(parent = game_frame)
        gui.pack(expand = True, fill = "both")
        engine = CubeeEngine(model)
        controller = CubeeController(engine = engine, gui = gui)
        controller.run()

        self._add_back_button(game_frame)

    def start_pixelkart(self, player1: PixelKartPlayer, player2: PixelKartPlayer, circuit_name: str, number_of_laps: int):
        self.hide_menu()

        game_frame = tk.Frame(self.parent, bg="#2C3E50")
        game_frame.pack(fill="both", expand=True)
        self.current_game_frame = game_frame

        # Use DAO for loading
        grid = dao.get_by_name(circuit_name)
        if not grid:
            messagebox.showerror("Error", f"Could not load circuit '{circuit_name}'")
            self.back_to_menu(game_frame)
            return

        rows = len(grid)
        cols = len(grid[0])
        board = PixelKartBoard(rows, cols)

        # Map the 2D list from the pickle file directly into the Board object
        for r in range(rows):
            for c in range(cols):
                board[(r, c)] = grid[r][c]

        logger.debug(f"Loaded circuit '{circuit_name}' with size {rows}x{cols}")

        model = PixelKartModel(board, player1, player2, laps_required=number_of_laps)
        
        gui = PixelKartGUI(parent=game_frame)
        gui.pack(expand=True, fill="both")
        engine = PixelKartEngine(model)
        controller = PixelKartController(engine, gui)
        controller.run()

        self._add_back_button(game_frame)

    def back_to_menu(self, frame_to_destroy: tk.Frame):
        """
        Destroy the current game frame and return to the main menu.

        Args:
            frame_to_destroy: The game frame to destroy.
        """
        frame_to_destroy.destroy()
        self.show_menu()

    def _add_back_button(self, game_frame: tk.Frame):
        """Add a 'Back to menu' button to the game frame."""
        back_btn = tk.Button(game_frame, text="Back to menu",
                             command=lambda: self.back_to_menu(game_frame),
                             bg="#3498DB", fg="#FFFFFF", activebackground="#2980B9", activeforeground="#FFFFFF")
        back_btn.place(x=20, y=20)

    def open_matches_settings(self):
        """Open the settings dialog for the Matches game."""
        available_players = self.players["matches"]
        player_names = list(available_players.keys())
        MatchesSettings(self.parent, player_names, self)

    def open_cubee_settings(self):
        """Open the settings dialog for the Cubee game."""
        available_players = self.players["cubee"]
        player_names = list(available_players.keys())
        CubeeSettings(self.parent, player_names, self)

    def open_pixelkart_settings(self):
        """Open the settings dialog for the PixelKart game."""
        available_players = self.players["pixel_kart"]
        player_names = list(available_players.keys())
        PixelKartSettings(self.parent, player_names, self)

class BaseSettings(tk.Toplevel):
    """Base class for game settings dialogs."""
    def __init__(self, parent, player_names: list[str], main_view: MainView, title: str):
        super().__init__(parent)
        self.parent = parent
        self.player_names = player_names
        self.main_view = main_view
        self.title(title)
        self.geometry("400x250")
        self.configure(bg="#2C3E50")

        self.p1_var = tk.StringVar(value=player_names[0] if player_names else "")
        self.p2_var = tk.StringVar(value=player_names[1] if len(player_names) > 1 else "")

        tk.Label(self, text="Player 1", bg="#2C3E50", fg="#FFFFFF").pack(pady=5)
        tk.OptionMenu(self, self.p1_var, *player_names).pack(pady=5)

        tk.Label(self, text="Player 2", bg="#2C3E50", fg="#FFFFFF").pack(pady=5)
        tk.OptionMenu(self, self.p2_var, *player_names).pack(pady=5)

        tk.Button(
            self, text="Play", command=self.play,
            bg="#3498DB", fg="#FFFFFF", activebackground="#2980B9", activeforeground="#FFFFFF"
        ).pack(pady=20)

    def play(self):
        """Validate and play the game (override in subclasses)."""
        raise NotImplementedError("Subclasses must implement play()")

    def validate_players(self) -> tuple[str, str]:
        """Validate that two different players are selected."""
        p1_name = self.p1_var.get()
        p2_name = self.p2_var.get()
        if p1_name == p2_name:
            messagebox.showerror("Error", "Players must be different.")
            return None, None
        return p1_name, p2_name

class MatchesSettings(BaseSettings):
    def __init__(self, parent, player_names: list[str], main_view: MainView):
        super().__init__(parent, player_names, main_view, "Matches Game Settings")

    def play(self):
        p1_name, p2_name = self.validate_players()
        if not p1_name:
            return
        
        player1 = self.main_view.players["matches"][p1_name]
        player2 = self.main_view.players["matches"][p2_name]
        
        self.main_view.start_allumettes(player1, player2)
        self.destroy()

class CubeeSettings(BaseSettings):
    def __init__(self, parent, player_names: list[str], main_view: MainView):
        super().__init__(parent, player_names, main_view, "Cubee Game Settings")

    def play(self):
        p1_name, p2_name = self.validate_players()
        if not p1_name:
            return

        player1 = self.main_view.players["cubee"][p1_name]
        player2 = self.main_view.players["cubee"][p2_name]
        
        self.main_view.start_cubee(player1, player2)
        self.destroy()

class PixelKartSettings(BaseSettings):
    def __init__(self, parent, player_names: list[str], main_view: MainView):
        # Silently migrate the old .txt files to the new .pkl system
        dao.import_legacy_txt()

        super().__init__(parent, player_names, main_view, "PixelKart Game Settings")
        self.geometry("400x420") # Increased height to fit the new UI elements

        def only_digits(new_value):
            # allow empty (so backspace works)
            if new_value == "":
                return True
            return new_value.isdigit()
        
        vcmd = (self.register(only_digits), "%P")
        
        # Number of laps
        tk.Label(self, text="Number of laps", bg="#2C3E50", fg="#FFFFFF").pack(pady=(10, 2))
        self.laps_entry = tk.Entry(self, validate="key", validatecommand=vcmd)
        self.laps_entry.insert(0, "1")
        self.laps_entry.pack(pady=5)

        # Circuit Selection UI
        tk.Label(self, text="Select Circuit", bg="#2C3E50", fg="#FFFFFF").pack(pady=(5, 2))

        self.circuit_var = tk.StringVar()
        self.circuit_dropdown = ttk.Combobox(self, textvariable=self.circuit_var, state="readonly")
        self.circuit_dropdown.pack(pady=5)
        
        # Editor Launch Button
        tk.Button(
            self, text="Open Circuit Editor", command=self.open_editor,
            bg="#27AE60", fg="#FFFFFF", activebackground="#2ECC71"
        ).pack(pady=10)

        # Populate the dropdown
        self.refresh_circuits()

    def refresh_circuits(self):
        """Updates the dropdown with available circuits from the DAO."""
        circuits = list(dao.get_all().keys())
        self.circuit_dropdown['values'] = circuits
        if circuits:
            # If nothing is selected, or the selected one was deleted, pick the first one
            if self.circuit_var.get() not in circuits:
                self.circuit_dropdown.set(circuits[0])

    def open_editor(self):
        """Launches the Circuit Editor and locks focus to it."""
        # We pass self.refresh_circuits so the editor can update this dropdown when you click 'Save'
        editor = CircuitEditor(self, on_close_callback=self.refresh_circuits)
        editor.grab_set() # Prevents the user from clicking the Settings menu while the Editor is open

    def play(self):
        """Overrides BaseSettings to include the circuit parameter."""
        player1_name, player2_name = self.validate_players()
        if not player1_name:
            return
            
        circuit_name = self.circuit_var.get()
        if not circuit_name:
            messagebox.showerror("Error", "Please select a circuit to play. If none exist, open the Editor to create one!")
            return
        
        player1 = self.main_view.players["pixel_kart"][player1_name]
        player2 = self.main_view.players["pixel_kart"][player2_name]
        number_of_laps = self.laps_entry.get()
        number_of_laps = int(number_of_laps) if number_of_laps else 1

        # Pass the circuit_name string to start_pixelkart instead of a hardcoded tuple
        self.main_view.start_pixelkart(player1, player2, circuit_name, number_of_laps)
        self.destroy()
