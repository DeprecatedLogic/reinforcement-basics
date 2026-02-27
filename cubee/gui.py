import tkinter as tk

class GUI(tk.Frame):
    """ Tkinter-based graphical user interface for the game `Cubee`. """
    def __init__(self, parent):
        """
        Initialize the GUI window and its components.
        """
        super().__init__(parent)

        self.board_frame = tk.Frame(self)
        self.board_frame.pack()

        self.buttons_frame = tk.Frame(self)
        self.buttons_frame.pack(pady=20)

    def create_board(self, rows, cols, on_cell_click) -> None:
        """
        TODO
        """
        for widget in self.board_frame.winfo_children():
            widget.destroy()

        self.board_buttons = []

        for row in range(rows):
            row_buttons = []
            for col in range(cols):
                btn = tk.Button(
                    self.board_frame,
                    text="",
                    command=lambda r=row, c=col: on_cell_click(r, c)
                )
                btn.grid(row=row, column=col, sticky="nsew")
                row_buttons.append(btn)

            self.board_buttons.append(row_buttons)

        # Resize
        for row in range(rows):
            self.board_frame.grid_rowconfigure(row, weight=1)

        for col in range(cols):
            self.board_frame.grid_columnconfigure(col, weight=1)

    def create_action_buttons(self) -> None:
        """Create possible actions buttons (Up, Down, Left, Right)"""
        pass

    def end_game(self, button_command: function) -> None:
        """Replace action buttons with a 'Restart' button when game ends."""
        for widget in self.buttons_frame.winfo_children():
            widget.destroy()
        
        button_reset = tk.Button(
            self.buttons_frame, 
            text="Restart", 
            command=button_command
        )
        button_reset.pack()