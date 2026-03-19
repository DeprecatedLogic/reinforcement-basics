from cubee.colors import Color
import tkinter as tk

class GUI(tk.Frame):
    """ Tkinter-based graphical user interface for the game `Cubee`. """
    def __init__(self, parent):
        """Initialize the GUI window and its components.

        Args:
            parent: _description_
        """

        # TODO: use the Color class for BG/FG (?)
        super().__init__(parent)
        self.configure(bg="#2C3E50")
        
        self.board_frame = tk.Frame(self, bg="#2C3E50")
        self.board_frame.pack()

        self.bottom_label = tk.Label(self, text = "Starting Game...", bg="#2C3E50", fg="#FFFFFF")
        self.bottom_label.pack(side = "bottom")

    def create_board(self, rows: int, columns: int, on_cell_click) -> None:
        """_summary_
        
        Args:
            rows (int): _description_
            columns (int): _description_
            on_cell_click: _description_
        """
        for widget in self.board_frame.winfo_children():
            widget.destroy()

        self.board_buttons = []

        for row in range(rows):
            row_buttons = []
            for col in range(columns):
                btn = tk.Button(
                    self.board_frame,
                    text=" ",
                    width=4,
                    height=2,
                    bg=Color.EMPTY.value,
                    command=lambda r=row, c=col: on_cell_click(r, c) if on_cell_click else None
                )
                btn.grid(row=row, column=col, sticky="nsew")
                row_buttons.append(btn)

            self.board_buttons.append(row_buttons)

        # Resize
        for row in range(rows):
            self.board_frame.grid_rowconfigure(row, weight=1)

        for col in range(columns):
            self.board_frame.grid_columnconfigure(col, weight=1)

    def update_turn_message(self, message: str) -> None:
        """_summary_

        Args:
            message (str): _description
        """
        self.bottom_label.config(text = message)

    def update_cell(self, row: int, col: int, label: str, color: Color | None) -> None:
        """_summary_

        Args:
            row (int): _description
            col (int): _description
            label (str): _description
            color (Color | None): _description
        """
        button = self.board_buttons[row][col]
        if color is not None:
            button.config(text = label, bg = color.value)
        else:
            button.config(text = label)

    def update_board(self, cells: list[tuple[int, int]], color: Color) -> None:
        """_summary_

        Args:
            cells (list[tuple[int, int]]): _description_
            color (Color): _description_
        """
        for cell in cells:
            row, col = cell
            self.board_buttons[row][col].config(bg = color.value)

    def end_game(self, button_command) -> None:
        """Replace action buttons with a 'Restart' button when game ends.
        
        Args:
            button_command: _description_
        """
        for widget in self.board_frame.winfo_children():
            widget.destroy()
        
        button_reset = tk.Button(
            self.board_frame, 
            text="Restart", 
            command=button_command
        )
        button_reset.pack()