import tkinter as tk
from tkinter import ttk, messagebox
import pixel_kart.dao as dao
from pixel_kart.cells import Cell, CELL_TO_COLOR, CELL_TO_LABEL, TERRAIN_BITMASK, SPECIAL_BITMASK

class CircuitEditor(tk.Toplevel):
    """
    Unified GUI for creating, editing, saving, and loading Pixel Kart circuits.
    Operates entirely on a 2D array of Cell Enums.
    """
    def __init__(self, parent, on_close_callback=None):
        """_summary_

        Args:
            parent (_type_): _description_
            on_close_callback (_type_, optional): _description_. Defaults to None.
        """
        super().__init__(parent)
        self.title("Pixel Kart - Circuit Editor")
        self.configure(bg="#2C3E50")
        self.on_close_callback = on_close_callback

        # Track the raw Enum data, not just the Tkinter widgets
        self.grid_state: list[list[Cell]] = []
        self.cell_labels: list[list[tk.Label]] = []
        
        # The order cells will cycle when clicked
        # The base terrain that makes up the track
        self.terrain_cycle = [Cell.GRASS, Cell.ROAD, Cell.WALL]
        
        # The special overlays (0 means none)
        self.special_cycle = [0, Cell.START_LINE, Cell.FINISH_LINE, Cell.CHECKPOINT]
        
        # Bitmasks to help us separate terrain from specials
        TERRAIN_BITMASK = Cell.GRASS | Cell.ROAD | Cell.WALL
        SPECIAL_BITMASK = Cell.START_LINE | Cell.FINISH_LINE | Cell.CHECKPOINT

        self._build_ui()
        self._init_blank_grid(12, 20) # Default size
        self._refresh_dropdown()

    def _build_ui(self):
        """Builds the control panels at the top and bottom of the window."""
        # === Top Panel: Resizing ===
        top_frame = tk.Frame(self, bg="#2C3E50")
        top_frame.pack(pady=10, fill="x", padx=10)

        tk.Label(top_frame, text="Rows:", bg="#2C3E50", fg="white").pack(side="left")
        self.rows_var = tk.StringVar(value="12")
        tk.Entry(top_frame, textvariable=self.rows_var, width=5).pack(side="left", padx=5)

        tk.Label(top_frame, text="Cols:", bg="#2C3E50", fg="white").pack(side="left")
        self.cols_var = tk.StringVar(value="20")
        tk.Entry(top_frame, textvariable=self.cols_var, width=5).pack(side="left", padx=5)

        tk.Button(top_frame, text="Resize Grid", command=self._handle_resize, 
                  bg="#3498DB", fg="white").pack(side="left", padx=10)

        # === Middle Panel: The Grid ===
        self.grid_frame = tk.Frame(self, bg="black", bd=2)
        self.grid_frame.pack(pady=10, padx=10, expand=True)

        # === Bottom Panel: Save & Load ===
        bottom_frame = tk.Frame(self, bg="#2C3E50")
        bottom_frame.pack(pady=10, fill="x", padx=10)

        # Load Section
        tk.Label(bottom_frame, text="Load Circuit:", bg="#2C3E50", fg="white").pack(side="left")
        self.selected_circuit = tk.StringVar()
        self.dropdown = ttk.Combobox(bottom_frame, textvariable=self.selected_circuit, state="readonly")
        self.dropdown.pack(side="left", padx=5)
        tk.Button(bottom_frame, text="Load", command=self._handle_load, 
                  bg="#27AE60", fg="white").pack(side="left", padx=5)

        # Spacer
        tk.Label(bottom_frame, text=" | ", bg="#2C3E50", fg="white").pack(side="left", padx=10)

        # Save Section
        tk.Label(bottom_frame, text="Save As:", bg="#2C3E50", fg="white").pack(side="left")
        self.save_name_var = tk.StringVar()
        tk.Entry(bottom_frame, textvariable=self.save_name_var, width=15).pack(side="left", padx=5)
        tk.Button(bottom_frame, text="Save", command=self._handle_save, 
                  bg="#E74C3C", fg="white").pack(side="left", padx=5)

    def _init_blank_grid(self, rows: int, columns: int):
        """
        Generates a new grid with Grass borders and Road in the middle.

        Args:
            rows (int): _description_
            columns (int): _description_
        """
        grid_data = []
        for row in range(rows):
            row_data = []
            for column in range(columns):
                if row == 0 or row == rows - 1 or column == 0 or column == columns - 1:
                    row_data.append(Cell.GRASS)
                else:
                    row_data.append(Cell.ROAD)
            grid_data.append(row_data)
            
        self._render_grid(grid_data)

    def _render_grid(self, grid_data: list[list[Cell]]):
        """
        Destroys the old Tkinter widgets and draws the new grid from data.

        Args:
            grid_data (list[list[Cell]]): _description_
        """
        # Clear existing widgets
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        self.grid_state = grid_data
        self.cell_labels = []

        rows = len(grid_data)
        cols = len(grid_data[0])

        for row in range(rows):
            label_row = []
            for column in range(cols):
                cell_type = grid_data[row][column]
                
                terrain_only = cell_type & TERRAIN_BITMASK
                special_only = cell_type & SPECIAL_BITMASK

                # Extract the string value from the Color Enum
                bg_color = CELL_TO_COLOR[terrain_only].value
                
                # Add a character for special tiles so they are visible
                text = CELL_TO_LABEL.get(special_only, "")

                lbl = tk.Label(self.grid_frame, bg=bg_color, text=text, width=2, height=1, 
                               borderwidth=1, relief="solid", font=("Courier", 12))
                lbl.grid(row=row, column=column, sticky="nsew")
                
                # Bind the click event, locking in current r and c values
                # Bind Left-Click for terrain
                lbl.bind("<Button-1>", lambda e, r=row, c=column: self._on_left_click(r, c))
                # Bind Right-Click for specials (Button-3 on Windows/Linux, Button-2/3 on Mac)
                lbl.bind("<Button-2>", lambda e, r=row, c=column: self._on_right_click(r, c)) # TODO: Remove bind? IDK if it works on Mac, I can't test
                lbl.bind("<Button-3>", lambda e, r=row, c=column: self._on_right_click(r, c))
                
                label_row.append(lbl)
                
            self.cell_labels.append(label_row)

        # Update the size text entries to match current grid
        self.rows_var.set(str(rows))
        self.cols_var.set(str(cols))

    def _on_left_click(self, row: int, column: int):
        """
        Cycles the base terrain (Grass -> Road -> Wall) without removing specials.

        Args:
            row (int): _description_
            column (int): _description_
        """
        current_cell = self.grid_state[row][column]
        
        # Extract the two halves
        current_terrain = current_cell & TERRAIN_BITMASK
        current_special = current_cell & SPECIAL_BITMASK
        
        # Cycle the terrain
        try:
            current_index = self.terrain_cycle.index(current_terrain)
        except ValueError:
            current_index = 0
            
        next_terrain = self.terrain_cycle[(current_index + 1) % len(self.terrain_cycle)]
        
        # Combine the new terrain with the old special item
        new_cell = next_terrain | current_special
        self._update_cell_visuals(row, column, new_cell)

    def _on_right_click(self, row: int, column: int):
        """
        Cycles the special overlay (None -> Start -> Finish -> Checkpoint) without removing terrain.

        Args:
            row (int): _description_
            column (int): _description_
        """
        current_cell = self.grid_state[row][column]
        
        current_terrain = current_cell & TERRAIN_BITMASK
        current_special = current_cell & SPECIAL_BITMASK
        
        # Cycle the special item
        try:
            current_index = self.special_cycle.index(current_special)
        except ValueError:
            current_index = 0
            
        next_special = self.special_cycle[(current_index + 1) % len(self.special_cycle)]
        
        # Combine the old terrain with the new special item
        new_cell = current_terrain | next_special
        self._update_cell_visuals(row, column, new_cell)

    def _update_cell_visuals(self, row: int, column: int, new_cell: Cell):
        """
        Updates the backend state and repaints the Tkinter label.

        Args:
            row (int): _description_
            column (int): _description_
            new_cell (Cell): _description_
        """
        self.grid_state[row][column] = new_cell
        
        terrain_only = new_cell & TERRAIN_BITMASK
        special_only = new_cell & SPECIAL_BITMASK
        
        bg_color = CELL_TO_COLOR[terrain_only].value
        text = CELL_TO_LABEL.get(special_only, "")
            
        self.cell_labels[row][column].config(bg=bg_color, text=text)

    def _handle_resize(self):
        """_summary_

        Raises:
            ValueError: _description_
        """
        try:
            row = int(self.rows_var.get())
            column = int(self.cols_var.get())
            if row < 5 or column < 5:
                raise ValueError
            self._init_blank_grid(row, column)
        except ValueError:
            messagebox.showerror("Error", "Rows and Cols must be integers >= 5")

    def _handle_save(self):
        """_summary_
        """
        name = self.save_name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a circuit name to save.")
            return

        # === Validation Check ===
        has_start = has_finish = has_checkpoint = False
        for row in self.grid_state:
            for cell in row:
                if cell & Cell.START_LINE: has_start = True
                elif cell & Cell.FINISH_LINE: has_finish = True
                elif cell & Cell.CHECKPOINT: has_checkpoint = True

        missing = []
        if not has_start: missing.append("Start Line (🏁)")
        if not has_finish: missing.append("Finish Line (🚩)")
        if not has_checkpoint: missing.append("Checkpoint (⭐)")

        if missing:
            messagebox.showerror("Validation Error", f"Cannot save! The circuit is missing:\n" + "\n".join(missing))
            return

        try:
            # Overwrite if it exists, otherwise save new
            existing = dao.get_all()
            if name in existing:
                if messagebox.askyesno("Overwrite", f"'{name}' already exists. Overwrite?"):
                    dao.update_circuit(name, self.grid_state)
                else:
                    return
            else:
                dao.save_circuit(name, self.grid_state)
                
            messagebox.showinfo("Success", f"Circuit '{name}' saved!")
            self._refresh_dropdown()
            self.dropdown.set(name) # Select the newly saved item
            
            if self.on_close_callback:
                self.on_close_callback() # Notify settings menu to update its list
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

    def _handle_load(self):
        """_summary_
        """
        name = self.selected_circuit.get()
        if not name:
            return
            
        grid = dao.get_by_name(name)
        if grid:
            self._render_grid(grid)
            self.save_name_var.set(name) # populate save box with loaded name

    def _refresh_dropdown(self):
        """_summary_
        """
        circuits = list(dao.get_all().keys())
        self.dropdown['values'] = circuits
        if circuits:
            self.dropdown.set(circuits[0])