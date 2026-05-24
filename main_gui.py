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
from pixel_kart import circuit_dao as dao
from pixel_kart.circuit_editor import CircuitEditor
# === Other Modules ===
import configparser
import os
import tkinter as tk
from tkinter import ttk, messagebox
import logging
logger = logging.getLogger(__name__)

class MainView(tk.Frame):
    """
    Central hub view container managing game profile options and configuration menu launchers.

    Acts as the main application entrance layout panel, rendering individual game selection 
    triggers and coordinating transition workflows into specialized active engine instances.
    """

    def __init__(self, parent, players: dict[dict[Player]]) -> None:
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

        self.parent.title("Projet IA")
        self.parent.geometry("700x500")
        self.parent.resizable(False, False)
        self.parent.configure(bg="#2C3E50")  # Dark blue-gray background

        self.create_menu_frame()
        self.show_menu()

    def create_menu_frame(self) -> None:
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

    def show_menu(self) -> None:
        """Display the menu frame and hide any active game frame."""
        if self.current_game_frame:
            self.current_game_frame.pack_forget()
        self.menu_frame.pack(expand=True)

    def hide_menu(self) -> None:
        """Hide the menu frame from the view."""
        self.menu_frame.pack_forget()

    def start_allumettes(self, player1: Player, player2: Player) -> None:
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

    def start_cubee(self, player1: CubeePlayer, player2: CubeePlayer) -> None:
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

    def show_pixelkart_help(self) -> None:
        """Display the gameplay instructions and controls modal for Pixel Kart."""

        help_text = (
            "CONTROLS & RULES\n\n"
            "HOW TO PLAY:\n"
            "  - Cross the Checkpoint (⭐) first, then race to the Finish Line (🚩)!\n\n"
            "ACTIONS:\n"
            "  - W: Accelerate\n"
            "  - A: Turn left\n"
            "  - D: Turn right\n"
            "  - S: Brake\n"
            "  - Space / Enter: Do nothing (continue)\n\n"
            "Note: Arrow keys work the same way as WASD."
        )
        messagebox.showinfo("Game Instructions", help_text)

    def start_pixelkart(
        self, player1: PixelKartPlayer, player2: PixelKartPlayer,
        circuit_name: str, number_of_laps: int
    ) -> bool:
        """
        Validate, parse, and launch the PixelKart game instance with the selected circuit.

        Args:
            player1: First player instance.
            player2: Second player instance.
            circuit_name: Key identifier of the circuit to pull from the data access object.
            number_of_laps: Total loop completion requirements for the game model.

        Returns:
            bool: True if initiation and track verification succeeded, False otherwise.
        """
        # Use DAO for loading
        grid = dao.get_by_name(circuit_name)
        if not grid:
            messagebox.showerror("Error", f"Could not load circuit '{circuit_name}'")
            # self.back_to_menu(game_frame)
            return False
        
        # Validate `START_LINE` cells before playing
        # (avoid raising an exception... refer to Model init)
        start_count = sum(1 for row in grid for cell in row if cell & Cell.START_LINE) # count total `START_LINE` cells
        if start_count < 2:
            messagebox.showerror(
                "Error", f"Circuit '{circuit_name}' only has {start_count} START_LINE (🏁) cells.\nYou need at least 2 to race! Please edit it."
            )
            # self.back_to_menu(game_frame)
            return False
        
        self.hide_menu()

        # First-time config check
        config_path = "config.ini"
        config = configparser.ConfigParser()
        config.read(config_path)

        # Check for PixelKart section in the config file (add it if not found)
        if not config.has_section("PixelKart"):
            config.add_section("PixelKart")
            
        # Check for `help_shown` in the `PixelKart` section (if not found, by default returns False)
        if not config.getboolean("PixelKart", "help_shown", fallback=False):
            self.show_pixelkart_help()
            
            # User saw the help message once, don't show again next time
            config.set("PixelKart", "help_shown", "True") 
            with open(config_path, "w") as configfile:
                config.write(configfile)

        game_frame = tk.Frame(self.parent, bg="#2C3E50")
        game_frame.pack(fill="both", expand=True)
        self.current_game_frame = game_frame

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

        # Pass the help command so the back button row can render the Help button
        self._add_back_button(game_frame, help_command=self.show_pixelkart_help)
        return True

    def back_to_menu(self, frame_to_destroy: tk.Frame):
        """
        Destroy the current game frame and return to the main menu view.

        Args:
            frame_to_destroy: The active game container frame to tear down.
        """
        frame_to_destroy.destroy()
        self.show_menu()

    def _add_back_button(self, game_frame: tk.Frame, help_command=None) -> None:
        """Add a 'Back to menu' button (and optionally a Help button) to the game frame."""
        back_btn = tk.Button(
            game_frame, text="Back to menu", command=lambda: self.back_to_menu(game_frame),
            bg="#3498DB", fg="#FFFFFF", activebackground="#2980B9", activeforeground="#FFFFFF"
        )
        back_btn.place(x=5, y=5)
        
        if help_command:
            help_btn = tk.Button(
                game_frame, text="Help", command=help_command,
                bg="#F39C12", fg="#FFFFFF", activebackground="#D68910", activeforeground="#FFFFFF"
            )
            help_btn.place(x=130, y=5) # next to the back button

    def open_matches_settings(self) -> None:
        """Open the initialization configuration dialog for the Matches game."""
        available_players = self.players["matches"]
        player_names = list(available_players.keys())
        MatchesSettings(self.parent, player_names, self)

    def open_cubee_settings(self) -> None:
        """Open the initialization configuration dialog for the Cubee game."""
        available_players = self.players["cubee"]
        player_names = list(available_players.keys())
        CubeeSettings(self.parent, player_names, self)

    def open_pixelkart_settings(self) -> None:
        """Open the initialization configuration dialog for the PixelKart game."""
        available_players = self.players["pixel_kart"]
        player_names = list(available_players.keys())
        PixelKartSettings(self.parent, player_names, self)

class BaseSettings(tk.Toplevel):
    """Base class architectural template managing setup selections for game loops."""

    def __init__(self, parent, player_names: list[str], main_view: MainView, title: str) -> None:
        """
        Initialize the structural parameters and common selectors of the settings window.

        Args:
            parent: The root Tkinter container reference window.
            player_names: Text string identifiers matching compatible strategy profiles.
            main_view: Hub application controller reference directing frame swaps.
            title: The descriptive window frame name string display.
        """
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
            bg="#2980B9", fg="#FFFFFF", activebackground="#3498DB"
        ).pack(pady=20)

    def play(self) -> None:
        """
        Validate profile variables and deploy specialized engines.

        Raises:
            NotImplementedError: If evaluated through base instance scope.
        """
        raise NotImplementedError("Subclasses must implement play()")

    def validate_players(self) -> tuple[str, str]:
        """
        Verify distinct identities for selected player profiles.

        Returns:
            tuple: A pair containing (player1_name, player2_name) if unique, 
                   otherwise (None, None).
        """
        p1_name = self.p1_var.get()
        p2_name = self.p2_var.get()
        if p1_name == p2_name:
            messagebox.showerror("Error", "Players must be different.")
            return None, None
        return p1_name, p2_name

class MatchesSettings(BaseSettings):
    """Specialized controller dialog configuring player parameters for the Matches variant."""

    def __init__(self, parent, player_names: list[str], main_view: MainView) -> None:
        """Initialize Matches settings window."""
        super().__init__(parent, player_names, main_view, "Matches Game Settings")

    def play(self) -> None:
        """Resolve profiles and trigger the Matches runtime loop."""
        p1_name, p2_name = self.validate_players()
        if not p1_name:
            return
        
        player1 = self.main_view.players["matches"][p1_name]
        player2 = self.main_view.players["matches"][p2_name]
        
        self.main_view.start_allumettes(player1, player2)
        self.destroy()

class CubeeSettings(BaseSettings):
    """Specialized controller dialog configuring player parameters for the Cubee variant."""

    def __init__(self, parent, player_names: list[str], main_view: MainView) -> None:
        """Initialize Cubee settings window."""
        super().__init__(parent, player_names, main_view, "Cubee Game Settings")

    def play(self) -> None:
        """Resolve profiles and trigger the Cubee board environment."""
        p1_name, p2_name = self.validate_players()
        if not p1_name:
            return

        player1 = self.main_view.players["cubee"][p1_name]
        player2 = self.main_view.players["cubee"][p2_name]
        
        self.main_view.start_cubee(player1, player2)
        self.destroy()

class PixelKartSettings(BaseSettings):
    """Specialized configuration wizard exposing track assets, lap counts, and editor workflows."""

    def __init__(self, parent, player_names: list[str], main_view: MainView) -> None:
        """Initialize PixelKart settings window and sync circuit directories."""
        # Silently migrate the old .txt files to the new .pkl system
        dao.import_legacy_txt()

        super().__init__(parent, player_names, main_view, "PixelKart Game Settings")
        self.geometry("400x420") # Increased height to fit the new UI elements

        # Allow only digits as input for the laps
        def only_digits(new_value):
            # allow empty (so backspace works in case of single digit)
            if new_value == "":
                return True
            return new_value.isdigit()
        
        # Wrap the `only_digits` function in a Tcl-compatible command
        validate_command = (self.register(only_digits), "%P") # the `%P` is simply the "preview"
        # An example of how it works:
        # Current text is "1", we press "5", %P evaluates to "15", only_digits("15") is executed
        
        # Number of laps
        tk.Label(self, text="Number of laps", bg="#2C3E50", fg="#FFFFFF").pack(pady=(10, 2))
        self.laps_entry = tk.Entry(self, validate="key", validatecommand=validate_command)
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

    def refresh_circuits(self) -> None:
        """Sync dropdown option listings with current serialization registries from the storage layer."""
        circuits = list(dao.get_all().keys())
        self.circuit_dropdown['values'] = circuits
        if circuits:
            # If nothing is selected, or the selected one was deleted, pick the first one
            if self.circuit_var.get() not in circuits:
                self.circuit_dropdown.set(circuits[0])

    def show_editor_help(self):
        """Display operational control maps mapping editor interaction configurations."""
        help_text = (
            "PIXEL KART CIRCUIT EDITOR\n\n"
            "- Left-Click: Cycle terrain (Grass -> Road -> Wall).\n"
            "- Right-Click: Cycle special tiles (None -> Start -> Finish -> Checkpoint).\n\n"
            "Note: You MUST place at least 2 Start (🏁) tiles to race!"
        )
        messagebox.showinfo("Editor Instructions", help_text)

    def open_editor(self) -> None:
        """Launch the isolated circuit designer utility tool layout blocking focus to underlying windows."""

        # We pass self.refresh_circuits so the editor can update this dropdown when you click 'Save'
        editor = CircuitEditor(self, on_close_callback=self.refresh_circuits, help_command=self.show_editor_help)
        editor.grab_set() # Prevents the user from clicking the Settings menu while the Editor is open

        # First-time config check
        config_path = "config.ini"
        config = configparser.ConfigParser()
        config.read(config_path)

        # Check for PixelKart section in the config file (add it if not found)
        if not config.has_section("PixelKart"):
            config.add_section("PixelKart")
            
        # Check for `editor_help_shown` in the `PixelKart` section (if not found, by default returns False)
        if not config.getboolean("PixelKart", "editor_help_shown", fallback=False):
            self.show_editor_help()
            
            # User saw the help message once, don't show again next time
            config.set("PixelKart", "editor_help_shown", "True") 
            with open(config_path, "w") as configfile:
                config.write(configfile)

    def play(self) -> None:
        """Validate components, map structures, lap entries and start the race track execution frame."""
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

        # If no errors, start the game and destroy the settings window
        if self.main_view.start_pixelkart(player1, player2, circuit_name, number_of_laps):
            self.destroy()
