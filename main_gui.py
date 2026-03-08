import tkinter as tk
from tkinter import messagebox
from matches.game_controller import GameController
from matches.player import Human, Player
from cubee.controller import GameController as CubeeController
from cubee.engine import GameEngine as CubeeEngine
from cubee.gui import GUI as CubeeGUI
from cubee.model import GameModel as CubeeModel, Board as CubeeBoard
from cubee.player import Player as CubeePlayer, Human as CubeeHuman

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
        self.parent.title("Projet IA")
        
        self.current_game_frame = None
        
        self.create_menu_frame()
        self.show_menu()

    def create_menu_frame(self):
        """Create the main meny frame with game buttons and settings."""
        self.menu_frame = tk.Frame(self.parent, padx=40, pady=40)
        
        title = tk.Label(self.menu_frame, text="Projet IA", font=("Arial", 28, "bold"))
        title.pack(pady=(0, 40))

        games = [
            ("Allumettes", self.open_matches_settings),
            ("Cubeee", self.open_cubee_settings),
            ("PixelKart", self.open_pixelkart_settings)
        ]

        for name, command in games:
            btn = tk.Button(self.menu_frame, text=name, font=("Helvetica", 16),
                            width=15, height=2, command=command)
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

        game_frame = tk.Frame(self.parent)
        game_frame.pack(fill="both", expand=True)
        self.current_game_frame = game_frame
        
        GameController(player1, player2, nb_matches=21, parent=game_frame)
        
        self._add_back_button(game_frame)

    def start_cubeee(self, player1: CubeePlayer, player2: CubeePlayer):
        """
        Start the Cubeee game with selected players.

        Args:
            player1: First player instance.
            player2: Second player instance.
        """
        self.hide_menu()

        game_frame = tk.Frame(self.parent)
        game_frame.pack(fill="both", expand=True)
        self.current_game_frame = game_frame
    
        model = CubeeModel(
            board = CubeeBoard(rows = 15, columns = 10),
            players = [player1, player2]
        )

        gui = CubeeGUI(parent = game_frame)
        gui.pack(expand = True, fill = "both")
        engine = CubeeEngine(model)
        controller = CubeeController(engine = engine, gui = gui)

        self._add_back_button(game_frame)

    def start_pixelkart(self):
        """Start the PixelKart game (placeholder implementation)."""
        self.hide_menu()

        game_frame = tk.Frame(self.parent)
        game_frame.pack(fill="both", expand=True)
        self.current_game_frame = game_frame
    
        # TODO: Implement PixelKart game logic here.

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
                             command=lambda: self.back_to_menu(game_frame))
        back_btn.place(x=20, y=20)

    def open_matches_settings(self):
        """Open the settings dialog for the Matches game."""
        available_players = self.players["matches"]
        player_names = list(available_players.keys())
        MatchesSettings(self.parent, player_names, self)

    def open_cubee_settings(self):
        """Open the settings dialog for the Cubeee game."""
        available_players = self.players["cubee"]
        player_names = list(available_players.keys())
        CubeeSettings(self.parent, player_names, self)

    def open_pixelkart_settings(self):
        """Open the settings dialog for the PixelKart game (placeholder)."""
        # TODO: Define available players for PixelKart in main.py.
        available_players = self.players["pixelkart"]
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

        self.p1_var = tk.StringVar(value=player_names[0] if player_names else "")
        self.p2_var = tk.StringVar(value=player_names[1] if len(player_names) > 1 else "")

        tk.Label(self, text="Player 1").pack(pady=5)
        tk.OptionMenu(self, self.p1_var, *player_names).pack(pady=5)

        tk.Label(self, text="Player 2").pack(pady=5)
        tk.OptionMenu(self, self.p2_var, *player_names).pack(pady=5)

        tk.Button(self, text="Save", command=self.save).pack(pady=20)

    def save(self):
        """Validate and save settings (override in subclasses)."""
        raise NotImplementedError("Subclasses must implement save()")

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

    def save(self):
        p1_name, p2_name = self.validate_players()
        if not p1_name:
            return
        player1 = self.main_view.players["matches"][p1_name]
        player2 = self.main_view.players["matches"][p2_name]
        self.main_view.start_allumettes(player1, player2)
        self.destroy()

class CubeeSettings(BaseSettings):
    def __init__(self, parent, player_names: list[str], main_view: MainView):
        super().__init__(parent, player_names, main_view, "Cubeee Game Settings")

    def save(self):
        p1_name, p2_name = self.validate_players()
        if not p1_name:
            return
        player1 = self.main_view.players["cubee"][p1_name]
        player2 = self.main_view.players["cubee"][p2_name]
        self.main_view.start_cubeee(player1, player2)
        self.destroy()

class PixelKartSettings(BaseSettings):
    def __init__(self, parent, player_names: list[str], main_view: MainView):
        super().__init__(parent, player_names, main_view, "PixelKart Game Settings")

    def save(self):
        # TODO: Implement player selection if needed; for now, just start the game.
        self.main_view.start_pixelkart()
        self.destroy()