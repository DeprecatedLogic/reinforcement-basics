from cubee.colors import Color
import tkinter as tk

class GUI(tk.Frame):
    """Tkinter-based graphical user interface for the Cubee game."""

    def __init__(self, parent) -> None:
        """
        Initialize the GUI frame and its components.

        Args:
            parent: The parent Tkinter widget (usually the root window).
        """

        # TODO: use the Color class for BG/FG (?)
        super().__init__(parent)
        self.configure(bg="#2C3E50")
        
        self.board_frame = tk.Frame(self, bg="#2C3E50")
        self.board_frame.pack()

        self.bottom_label = tk.Label(self, text="Starting Game...", bg="#2C3E50", fg="#FFFFFF")
        self.bottom_label.pack(side="bottom")

    def create_board(self, rows: int, columns: int, on_cell_click) -> None:
        """
        Create the board layout with buttons for each cell.

        Args:
            rows (int): Number of rows in the board.
            columns (int): Number of columns in the board.
            on_cell_click (callable): Function to call when a cell is clicked.
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
        """
        Update the message label at the bottom of the GUI.

        Args:
            message (str): The message to display (e.g., current player's turn or game over).
        """
        self.bottom_label.config(text=message)

    def update_cell(self, row: int, col: int, label: str, color: Color | None) -> None:
        """
        Update a single cell's display.

        Args:
            row (int): Row index of the cell.
            col (int): Column index of the cell.
            label (str): Text to display in the cell.
            color (Color | None): Background color of the cell; if None, color is unchanged.
        """
        button = self.board_buttons[row][col]
        if color is not None:
            button.config(text=label, bg=color.value)
        else:
            button.config(text=label)

    def update_board(self, cells: list[tuple[int, int]], color: Color) -> None:
        """
        Update the background color of multiple cells (e.g., after enclosures).

        Args:
            cells (list[tuple[int, int]]): List of (row, column) positions to update.
            color (Color): The color to set for these cells.
        """
        for cell in cells:
            row, col = cell
            self.board_buttons[row][col].config(bg=color.value)

    def bind_keys(self, keypress_handler) -> None:
        """
        Bind a keypress handler to all keyboard events in the GUI.

        Args:
            keypress_handler (callable): Function to call on keypress events.
        """
        self.bind_all("<Key>", keypress_handler)

    def end_game(self, button_command) -> None:
        """
        Replace the board with a 'Restart' button and unbind key events.

        Args:
            button_command (callable): Function to execute when 'Restart' is pressed.
        """
        self.unbind_all("<Key>")

        for widget in self.board_frame.winfo_children():
            widget.destroy()
        
        button_reset = tk.Button(
            self.board_frame, 
            text="Restart", 
            command=button_command
        )
        button_reset.pack()