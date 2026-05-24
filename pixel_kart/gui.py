import tkinter as tk
from pixel_kart.cells import Cell, CELL_TO_COLOR, CELL_TO_LABEL, TERRAIN_BITMASK, SPECIAL_BITMASK
from pixel_kart.player import Player
import logging
logger = logging.getLogger(__name__)

class GUI(tk.Frame):
    """
    Tkinter interface layout rendering track grids and dashboard telemetry panels.

    Utilizes light matrix arrays of standard label widgets to map underlying cell maps,
    color overlays, and multi-agent position vectors without external image rendering dependencies.
    """
    def __init__(self, parent) -> None:
        """
        Initialize structural visual elements, background configurations, and tracking grids.

        Args:
            parent: The underlying root window thread or master Tkinter structural panel.
        """
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

    def create_board(self, grid: list[list[Cell]]) -> None:
        """
        Build the initial 2D label matrix grid matching track size dimensions.

        Args:
            board_grid (list[list[Cell]]): The layout matrix containing track cell flags.
        """
        rows = len(grid)
        cols = len(grid[0])
        
        self.labels = [[None for _ in range(cols)] for _ in range(rows)]
        self.base_texts = [[None for _ in range(cols)] for _ in range(rows)]
        
        for row in range(rows):
            for column in range(cols):
                cell_type = grid[row][column]
                terrain_only = cell_type & TERRAIN_BITMASK
                special_only = cell_type & SPECIAL_BITMASK

                # Determine background color
                bg_color = CELL_TO_COLOR[terrain_only].value
                
                # Determine text/icon
                base_text = CELL_TO_LABEL.get(special_only, "")

                # Do not show checkpoints (?)
                #if Cell.CHECKPOINT & special_only:
                #   base_text = ""
                    
                self.base_texts[row][column] = base_text
                
                # Create the label (Width/Height are in text units, not pixels)
                label = tk.Label(
                    self.grid_frame, text=base_text, font=("Courier", 18, "bold"),
                    bg=bg_color, fg="black", width=2, height=1, borderwidth=1, relief="solid"
                )
                label.grid(row=row, column=column)
                self.labels[row][column] = label

    def update_karts(self, players: list[Player]) -> None:
        """
        Redraw every active agent's directional symbol onto the track matrix grid layer.

        Note:
            Sweeps and resets prior state cell labels before overlaying fresh spatial mappings 
            to shield the interface view layer from artifacting loops.

        Args:
            players (list[Player]): Explicit collection containing every active participant profile.
        """
        # Clear the entire board of karts (restore to default text)
        for row in range(len(self.labels)):
            for column in range(len(self.labels[0])):
                current_text = self.labels[row][column].cget("text")
                base_text = self.base_texts[row][column]
                if current_text != base_text:
                    self.labels[row][column].config(text=base_text, fg="black")
        
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

    def update_hud(self, current_player: Player, laps_completed: dict) -> None:
        """
        Refresh numerical metrics displays on the bottom cockpit telemetry overlay panel.

        Args:
            current_player (Player): Active profile whose context data is currently evaluated.
            laps_completed (dict[Player, int]): Standings tracker mapping completed loops.
        """
        speed = current_player.speed
        laps = laps_completed.get(current_player, 0)
        self.stats_label.config(text=f"{current_player.name} | Speed: {speed} | Laps: {laps}")

    def update_turn_message(self, message: str) -> None:
        """
        Publish string data statements straight into the primary dashboard message bar.

        Args:
            message (str): Text message payload to be displayed.
        """
        self.turn_label.config(text=message)

    def bind_keys(self, keypress_handler) -> None:
        """
        Bind high-level global key intercept triggers to the top window frame components.

        Args:
            keypress_handler: Target function pointer invoked following standard keystrokes.
        """
        self.bind_all("<Key>", keypress_handler)

    def end_game(self, button_command) -> None:
        """
        Tear down keyboard event listeners and instantiate an absolute match ending overlay modal.

        Args:
            button_command: Target callback logic executed when restarting loops via button triggers.
        """
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