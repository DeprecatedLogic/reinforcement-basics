import tkinter as tk
from matches.game_controller import GameController
from matches.player import Human, Player
from cubee.controller import GameController as CubeeController
from cubee.engine import GameEngine as CubeeEngine
from cubee.gui import GUI as CubeeGUI
from cubee.model import GameModel as CubeeModel, Board as CubeeBoard
from cubee.player import Player as CubeePlayer, Human as CubeeHuman

class MainView(tk.Frame):
    def __init__(self, parent, player1=None, player2=None):
        super().__init__(parent)
        self.parent = parent
        self.parent.title("Projet IA")

        self.p1 = player1
        self.p2 = player2
        
        self.current_game_frame = None
        
        self.create_menu_frame()
        self.show_menu()

    def create_menu_frame(self):
        """Create the main meny frame with game buttons and settings."""
        self.menu_frame = tk.Frame(self.parent, padx=40, pady=40)
        
        title = tk.Label(self.menu_frame, text="Projet IA", font=("Arial", 28, "bold"))
        title.pack(pady=(0, 40))

        games = [
            ("Allumettes", self.start_allumettes),
            ("Cubeee",     self.start_cubeee),
            ("PixelKart",  self.start_pixelkart)  
        ]

        for name, command in games:
            btn = tk.Button(self.menu_frame, text=name, font=("Helvetica", 16),
                            width=15, height=2, command=command)
            btn.pack(pady=15)

    def show_menu(self):
        """Display the menu frame and hide any current game frame."""
        if self.current_game_frame:
            self.current_game_frame.pack_forget()
        self.menu_frame.pack(expand=True)

    def hide_menu(self):
        """Hide the menu frame"""
        self.menu_frame.pack_forget()
    
    def start_allumettes(self, player1: Player = Human("Player1"), player2: Player = Human("Player2")):
        """
        Start the matches game.

        Args:
            player1: First player (can be Human or AI)
            player2: Second player (can be Human or AI)

        """
        self.hide_menu()
        
        game_frame = tk.Frame(self.parent)
        game_frame.pack(fill="both", expand=True)
        
        self.current_game_frame = game_frame
        
        controller = GameController(player1, player2, nb_matches=21, parent=game_frame)
        
        back_btn = tk.Button(game_frame, text="Back to menu",
                             command=lambda: self.back_to_menu(game_frame))
        back_btn.place(x=20, y=20)

    def start_cubeee(self):
        self.hide_menu()

        game_frame = tk.Frame(self.parent)
        game_frame.pack(fill="both", expand=True)
        
        self.current_game_frame = game_frame
    
        model = CubeeModel(
            board = CubeeBoard(rows = 15, columns = 10),
            players = [CubeeHuman("Player1"), CubeeHuman("Player2")]
        )

        gui = CubeeGUI(parent = game_frame)
        gui.pack(expand = True, fill = "both")
        engine = CubeeEngine(model)
        controller = CubeeController(
            engine = engine,
            gui = gui
        )

        back_btn = tk.Button(game_frame, text="Back to menu",
                             command=lambda: self.back_to_menu(game_frame))
        back_btn.place(x=20, y=20)

    def start_pixelkart(self):
        """TODO"""
        self.hide_menu()

        game_frame = tk.Frame(self.parent)
        game_frame.pack(fill="both", expand=True)
        
        self.current_game_frame = game_frame
    
        #TODO

        back_btn = tk.Button(game_frame, text="Back to menu",
                             command=lambda: self.back_to_menu(game_frame))
        back_btn.place(x=20, y=20)

    def back_to_menu(self, frame_to_destroy):
        """
        Destroy the current game frame and return to the main menu.

        Args:
            frame_to_destroy: The game frame to destroy.
        """
        frame_to_destroy.destroy()
        self.show_menu()