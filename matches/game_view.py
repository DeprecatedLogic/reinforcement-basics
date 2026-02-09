import tkinter as tk

class GameView(tk.Tk):
    """Tkinter-based graphical user interface for the game of matches."""
    def __init__(self, controller):
        """
        Initialize the GUI window and its components.

        Args:
            controller: GameController instance that handles logic and state
        """
        super().__init__()
        self.controller = controller
        self.title("Jeu des Allumettes")

        self.counter = tk.Label(self, text="", font=("Arial", 14))
        self.counter.pack(pady=10)

        self.canvas = tk.Canvas(self, width=400, height=200, bg="white")
        self.canvas.pack(pady=20)

        self.message_label = tk.Label(self, text="", font=("Arial", 14))
        self.message_label.pack(pady=10)

        self.buttons_frame = tk.Frame(self)
        self.buttons_frame.pack(pady=20)

        self.reset()
        self.update_view()

    def update_view(self) -> None:
        """Refresh all visual elements based on current game state."""
        self.canvas.delete("all")
        nb_matches = self.controller.get_nb_matches()
        status_msg = self.controller.get_status_message()

        self.counter.config(text=f"{nb_matches} ({self.controller.action_taken} removed)")
        self.draw_matches(nb_matches)
        self.message_label.config(text=status_msg)

    def draw_matches(self, n) -> None:
        """
        Render the specified number of matches on the canvas.

        Args:
            n: Current number of remaining matches
        """
        width = 400
        margin = 20

        #Mathematical formula given by Gemini
        if n > 0:
            gap = (width - 2 * margin) / max(n, 1)
            for i in range(n):
                x = margin + i * gap
                self.canvas.create_line(x, 50, x, 150, width=5, fill="brown")
                self.canvas.create_oval(x-5, 40, x+5, 60, fill="red")

    def end_game(self) -> None:
        """Replace action buttons with a 'Restart' button when game ends."""
        for widget in self.buttons_frame.winfo_children():
            widget.destroy()
        
        button_reset = tk.Button(
            self.buttons_frame, 
            text="Restart", 
            command=self.controller.reset_game
        )
        button_reset.pack()

    def reset(self) -> None:
        """Recreate the three move buttons (1, 2, 3 matches)."""
        for widget in self.buttons_frame.winfo_children():
            widget.destroy()
            
        for i in range(1, 4):
            button = tk.Button(
                self.buttons_frame, 
                text=f"Remove {i}", 
                command=lambda val=i: self.controller.handle_human_move(val)
            )
            button.pack(side=tk.LEFT, padx=10)