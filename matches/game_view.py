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

        self.reset()
        self.update_view()

    def update_view(self):
        self.canvas.delete("all")
        nb_matches = self.controler.get_nb_matches()
        status_msg = self.controler.get_status_message()

        self.draw_matches(nb_matches)
        self.message_label.config(text=status_msg)

    def draw_matches(self, n):
        width = 400
        margin = 20

        #Mathematical formula given by Gemini
        if n > 0:
            gap = (width - 2 * margin) / max(n, 1)
            for i in range(n):
                x = margin + i * gap
                self.canvas.create_line(x, 50, x, 150, width=5, fill="brown")
                self.canvas.create_oval(x-5, 40, x+5, 60, fill="red")

    def end_game(self):
        for widget in self.buttons_frame.winfo_children():
            widget.destroy()
        
        button_reset = tk.Button(
            self.buttons_frame, 
            text="Recommencer", 
            command=self.controler.reset_game
        )
        button_reset.pack()

    def reset(self):
        for widget in self.buttons_frame.winfo_children():
            widget.destroy()
            
        for i in range(1, 4):
            button = tk.Button(
                self.buttons_frame, 
                text=f"Prendre {i}", 
                command=lambda val=i: self.controler.handle_human_move(val)
            )
            button.pack(side=tk.LEFT, padx=10)