import tkinter as tk
from matches.game_controller import GameController
from matches.player import Human, AI

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
        if self.current_game_frame:
            self.current_game_frame.pack_forget()
        self.menu_frame.pack(expand=True)

    def hide_menu(self):
        self.menu_frame.pack_forget()
    
    def start_allumettes(self):
        self.hide_menu()
        
        game_frame = tk.Frame(self.parent)
        game_frame.pack(fill="both", expand=True)
        
        self.current_game_frame = game_frame
        
        p1 = self.p1 or Human("Player1")
        p2 = self.p2 or Human("Player2")
        
        controller = GameController(p1, p2, nb_matches=21, parent=game_frame)
        
        back_btn = tk.Button(game_frame, text="Back to menu",
                             command=lambda: self.back_to_menu(game_frame))
        back_btn.place(x=20, y=20)

    def back_to_menu(self, frame_to_destroy):
        frame_to_destroy.destroy()
        self.show_menu()

    def start_cubeee(self):
        pass
    
    def start_pixelkart(self):
        pass
    
    def open_settings(self):
        pass