import tkinter as tk
from pixel_kart.cells import Cell, CELL_TO_COLOR, CELL_TO_LABEL, TERRAIN_BITMASK, SPECIAL_BITMASK
from pixel_kart.player import Player
import logging
logger = logging.getLogger(__name__)

class GUI(tk.Frame):
    """
    Tkinter GUI for Pixel Kart using a simple Label grid.
    No external image libraries required.
    """
    def __init__(self, parent):
        super().__init__(parent, bg="#2C3E50")
        self.parent = parent
        
        # HUD Frame (BOTTOM)
        self.hud_frame = tk.Frame(self, bg="#2C3E50")
        self.hud_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10, padx=20)
        
        self.turn_label = tk.Label(self.hud_frame, text="Initializing...", font=("Helvetica", 14, "bold"), bg="#2C3E50", fg="white")
        self.turn_label.pack(side=tk.LEFT)
        
        self.stats_label = tk.Label(self.hud_frame, text="Player Speed: 0 | Laps: 0", font=("Helvetica", 14), bg="#2C3E50", fg="#F1C40F")
        self.stats_label.pack(side=tk.RIGHT)
        
        # Grid Frame for the board
        self.grid_frame = tk.Frame(self, bg="black", bd=2)
        self.grid_frame.pack(expand=True)
        
        # 2D arrays to hold the Label widgets and the default text for each cell
        self.labels = []
        self.base_texts = [] 

        # Mapping direction index to text arrows
        self.direction_symbols = {
            0: "▲", # North
            1: "▶", # East
            2: "▼", # South
            3: "◀"  # West
        }

    def create_board(self, grid: list[list[Cell]]):
        """Draws the initial track using a grid of Tkinter Labels."""
        rows = len(grid)
        cols = len(grid[0])
        
        self.labels = [[None for _ in range(cols)] for _ in range(rows)]
        self.base_texts = [[None for _ in range(cols)] for _ in range(rows)]
        
        for r in range(rows):
            for c in range(cols):
                cell_type = grid[r][c]
                terrain_only = cell_type & TERRAIN_BITMASK
                special_only = cell_type & SPECIAL_BITMASK

                # Determine background color
                bg_color = CELL_TO_COLOR[terrain_only].value
                
                # Determine text/icon
                base_text = CELL_TO_LABEL.get(special_only, "")

                # Do not show checkpoints
                if Cell.CHECKPOINT & special_only:
                    base_text = ""
                    
                self.base_texts[r][c] = base_text
                
                # Create the label (Width/Height are in text units, not pixels)
                lbl = tk.Label(self.grid_frame, text=base_text, font=("Courier", 18, "bold"),
                               bg=bg_color, fg="black", width=2, height=1, borderwidth=1, relief="solid")
                lbl.grid(row=r, column=c)
                self.labels[r][c] = lbl

    def update_karts(self, players: list[Player]):
        """Wipes old karts by restoring base text, then draws karts at new positions."""
        # Clear the entire board of karts (restore to default terrain text)
        for r in range(len(self.labels)):
            for c in range(len(self.labels[0])):
                current_text = self.labels[r][c].cget("text")
                base_text = self.base_texts[r][c]
                if current_text != base_text:
                    self.labels[r][c].config(text=base_text, fg="black")
        
        # Draw the karts
        for player in players:
            row, col = player.position
            
            # Boundary check to prevent Tkinter index errors
            if 0 <= row < len(self.labels) and 0 <= col < len(self.labels[0]):
                if player.crashed:
                    symbol = "💥"
                else:
                    symbol = self.direction_symbols.get(player.direction_index, "O")
                    
                self.labels[row][col].config(text=symbol, fg=player.color.value)

    def update_hud(self, current_player: Player, laps_completed: dict):
        """Updates the speed and lap counters for the current player."""
        speed = current_player.speed
        laps = laps_completed.get(current_player, 0)
        self.stats_label.config(text=f"{current_player.name} | Speed: {speed} | Laps: {laps}")

    def update_turn_message(self, message: str) -> None:
        """Updates the top message bar."""
        self.turn_label.config(text=message)

    def bind_keys(self, keypress_handler) -> None:
        """Binds keyboard input to the main Tkinter window."""
        self.bind_all("<Key>", keypress_handler)

    def end_game(self, button_command) -> None:
        """Displays a game over overlay and unbinds the keys."""
        self.parent.unbind_all("<Key>")
        
        # Overlay frame using place() to center it over the grid
        overlay = tk.Frame(self.grid_frame, bg="#2C3E50", bd=5, relief=tk.RAISED)
        overlay.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=300, height=150)
        
        tk.Label(
            overlay, text="🏁 RACE FINISHED 🏁", font=("Helvetica", 16, "bold"),
            bg="#2C3E50", fg="white"
        ).pack(pady=10)
        tk.Button(
            overlay, text="Restart", command=button_command, 
            bg="#E74C3C", fg="white", font=("Helvetica", 12)
        ).pack(pady=10)