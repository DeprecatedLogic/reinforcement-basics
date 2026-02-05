import tkinter as tk

class GameView(tk.Tk):
    def __init__(self, controler):
        super().__init__()
        self.controler = controler
        self.title("Jeu des Allumettes")

        self.canvas = tk.Canvas(self, width=400, height=200, bg="white")
        self.canvas.pack(pady=20)

        self.message_label = tk.Label(self, text="", font=("Arial", 14))
        self.message_label.pack(pady=10)

        self.buttons_frame = tk.Frame(self)
        self.buttons_frame.pack(pady=20)

        self.update_view()

    def update_view(self):
        self.canvas.delete("all")
        nb_matches = self.controler.get_nb_matches()
        status_msg = self.controler.get_status_message()

        self.message_label.config(text=status_msg)

    def draw_matches(self, n):
        pass

    def end_game(self):
        pass

    def reset(self):
        pass