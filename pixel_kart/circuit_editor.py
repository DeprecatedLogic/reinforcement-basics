import tkinter as tk
from tkinter import ttk, messagebox
import pixel_kart.circuit_dao as dao
from pixel_kart.cells import Cell, CELL_TO_COLOR, CELL_TO_LABEL, TERRAIN_BITMASK, SPECIAL_BITMASK

class CircuitEditor(tk.Toplevel):
    """
    Unified GUI window subclass for creating, editing, saving, and loading Pixel Kart circuits.

    Operates entirely on a 2D matrix array of Cell Enums. Manages user click input bindings 
    to cycle independent layers of background terrain flags and overlaying special flags 
    simultaneously within single cell locations.
    """
    def __init__(self, parent, on_close_callback=None, help_command=None) -> None:
        """
        Initialize the circuit editor window layer and its corresponding matrix state vectors.

        Args:
            parent (tk.Tk | tk.Toplevel): The parent Tkinter window anchoring this dialog.
            on_close_callback (callable, optional): A zero-argument callback executed when a circuit 
                                                   is successfully saved, alerting the caller to refresh data. 
                                                   Defaults to None.
            help_command (callable, optional): A zero-argument callback tied to the window's "Help" button. 
                                               Defaults to None.
        """
        super().__init__(parent)
        self.title("Pixel Kart - Circuit Editor")
        self.configure(bg="#2C3E50")
        self.on_close_callback = on_close_callback
        self.help_command = help_command

        # Track the raw Enum data, not just the Tkinter widgets
        self.grid_state: list[list[Cell]] = []
        self.cell_labels: list[list[tk.Label]] = []
        
        # The order cells will cycle when clicked
        # The base terrain that makes up the track
        self.terrain_cycle = [Cell.GRASS, Cell.ROAD, Cell.WALL]
        
        # The special overlays (0 means none/empty)
        self.special_cycle = [0, Cell.START_LINE, Cell.FINISH_LINE, Cell.CHECKPOINT]

        self._build_ui()
        self._init_blank_grid(12, 20) # Default size
        self._refresh_dropdown()

    def _build_ui(self) -> None:
        """
        Construct and assemble the interface control zones.

        Generates layout grids for sizing fields and help controls at the window crown, 
        and configures database IO dropdown menus along with execution buttons at the base.
        """
        # Top Panel (Grid Size & Help)
        top_frame = tk.Frame(self, bg="#2C3E50")
        top_frame.pack(pady=10, fill="x", padx=10)

        tk.Label(top_frame, text="Rows:", bg="#2C3E50", fg="#FFFFFF").pack(side="left")
        self.rows_var = tk.StringVar(value="12")
        tk.Entry(top_frame, textvariable=self.rows_var, width=5).pack(side="left", padx=5)

        tk.Label(top_frame, text="Cols:", bg="#2C3E50", fg="#FFFFFF").pack(side="left")
        self.cols_var = tk.StringVar(value="20")
        tk.Entry(top_frame, textvariable=self.cols_var, width=5).pack(side="left", padx=5)

        tk.Button(
            top_frame, text="Resize Grid", command=self._handle_resize, 
            bg="#2980B9", fg="#FFFFFF", activebackground="#3498DB"
        ).pack(side="left", padx=10)

        if self.help_command:
            tk.Button(
                top_frame, text="Help", command=self.help_command, 
                bg="#F39C12", fg="#FFFFFF", activebackground="#D68910"
            ).pack(side="right", padx=0)

        # Middle Panel (The Grid)
        self.grid_frame = tk.Frame(self, bg="black", bd=2)
        self.grid_frame.pack(pady=10, padx=10, expand=True)

        # Bottom Panel (Save & Load)
        bottom_frame = tk.Frame(self, bg="#2C3E50")
        bottom_frame.pack(pady=10, fill="x", padx=10)

        # Load Section
        tk.Label(bottom_frame, text="Load Circuit:", bg="#2C3E50", fg="#FFFFFF").pack(side="left")
        self.selected_circuit = tk.StringVar()
        self.dropdown = ttk.Combobox(bottom_frame, textvariable=self.selected_circuit, state="readonly")
        self.dropdown.pack(side="left", padx=5)
        tk.Button(
            bottom_frame, text="Load", command=self._handle_load,
            bg="#27AE60", fg="#FFFFFF", activebackground="#2ECC71"
        ).pack(side="left", padx=5)
        tk.Button(
            bottom_frame, text="Delete", command=self._handle_delete,
            bg="#E74C3C", fg="#FFFFFF", activebackground="#FF6565"
        ).pack(side="left", padx=5)

        # Spacer
        tk.Label(bottom_frame, text=" | ", bg="#2C3E50", fg="#FFFFFF").pack(side="left", padx=10)

        # Save Section
        tk.Label(bottom_frame, text="Save As:", bg="#2C3E50", fg="#FFFFFF").pack(side="left")
        self.save_name_var = tk.StringVar()
        tk.Entry(bottom_frame, textvariable=self.save_name_var, width=15).pack(side="left", padx=5)
        tk.Button(
            bottom_frame, text="Save", command=self._handle_save,
            bg="#2980B9", fg="#FFFFFF", activebackground="#3498DB"
        ).pack(side="left", padx=5)

    def _init_blank_grid(self, rows: int, columns: int) -> None:
        """
        Generate a pristine workspace track matrix surrounded by grass borders.

        Note:
            Fills outer matrix row/col boundaries with `Cell.GRASS` and assigns internal 
            coordinates to `Cell.ROAD`. This state is passed directly to the rendering cycle.

        Args:
            rows (int): The total vertical row dimensions requested.
            columns (int): The total horizontal column dimensions requested.
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

    def _render_grid(self, grid_data: list[list[Cell]]) -> None:
        """
        Wipe out stale display components and systematically redraw the workspace grid layout.

        Note:
            Extracts individual cell segments using global terrain and special bitmasks. 
            Background colors correspond to active terrain variants, while text glyphs represent 
            special configurations. Mouse actions map index locks directly onto specific cell click handlers.

        Args:
            grid_data (list[list[Cell]]): The structural source matrix used to initialize layout widgets.
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
                lbl.bind("<Button-2>", lambda e, r=row, c=column: self._on_right_click(r, c))
                lbl.bind("<Button-3>", lambda e, r=row, c=column: self._on_right_click(r, c))
                
                label_row.append(lbl)
                
            self.cell_labels.append(label_row)

        # Update the size text entries to match current grid
        self.rows_var.set(str(rows))
        self.cols_var.set(str(cols))

    def _on_left_click(self, row: int, column: int) -> None:
        """
        Cycle the terrain layer step-by-step upon receiving primary cursor interactions.

        Note:
            Isolates the target item's terrain values from any overlapping functional 
            markers. Cycles the type across configured settings. If the destination 
            evaluates to `Cell.WALL`, overlapping assets are automatically dropped 
            to prevent structural clipping conflicts.

        Args:
            row (int): The row coordinate tracking the target layout cell.
            column (int): The column coordinate tracking the target layout cell.
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
        if next_terrain & Cell.WALL:
            current_special = 0

        # Combine the new terrain with the old special item
        new_cell = next_terrain | current_special
        self._update_cell_visuals(row, column, new_cell)

    def _on_right_click(self, row: int, column: int) -> None:
        """
        Cycle functional objective marker elements without mutating underlying terrain setups.

        Note:
            If a special tile maps onto a restrictive wall block, the system automatically 
            downgrades that block to a `Cell.ROAD` segment to ensure game loop logic operates smoothly.

        Args:
            row (int): The row coordinate tracking the target layout cell.
            column (int): The column coordinate tracking the target layout cell.
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
        if next_special & SPECIAL_BITMASK and current_terrain & Cell.WALL:
            current_terrain = Cell.ROAD

        # Combine the old terrain with the new special item
        new_cell = current_terrain | next_special
        self._update_cell_visuals(row, column, new_cell)

    def _update_cell_visuals(self, row: int, column: int, new_cell: Cell) -> None:
        """
        Apply a fresh configuration to the master matrix buffer and update widget displays.

        Args:
            row (int): The row coordinate tracking the modified layout cell.
            column (int): The column coordinate tracking the modified layout cell.
            new_cell (Cell): The updated unified flag composite state to apply.
        """
        self.grid_state[row][column] = new_cell
        
        terrain_only = new_cell & TERRAIN_BITMASK
        special_only = new_cell & SPECIAL_BITMASK
        
        bg_color = CELL_TO_COLOR[terrain_only].value
        text = CELL_TO_LABEL.get(special_only, "")
            
        self.cell_labels[row][column].config(bg=bg_color, text=text)

    def _handle_resize(self) -> None:
        """
        Parse matrix configuration parameters and regenerate the system workspace area.

        Note:
            Enforces layout constraints demanding minimum grid bounds of at least 5x5 cells.

        Raises:
            ValueError: If input components do not contain valid integer sequences, 
                        or violate minimum track aspect ratios.
        """
        try:
            row = int(self.rows_var.get())
            column = int(self.cols_var.get())
            if row < 5 or column < 5:
                raise ValueError
            self._init_blank_grid(row, column)
        except ValueError:
            messagebox.showerror("Error", "Rows and Cols must be integers >= 5")

    def _handle_save(self) -> None:
        """
        Validate track logic components and commit the active layout state to persistent storage.

        Note:
            Verifies that at least one instance of a Start Line, Finish Line, and Checkpoint 
            exists before committing data. If the workspace contains fewer than 2 start lines, 
            the output is automatically marked with a " (WIP)" tag to prevent deployment issues 
            in standard game loops while protecting existing WIP tags from duplicating.
        """
        name = self.save_name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a circuit name to save.")
            return

        # === Validation Check ===
        start_count = 0
        has_finish = has_checkpoint = False
        for row in self.grid_state:
            for cell in row:
                if cell & Cell.START_LINE: start_count += 1
                if cell & Cell.FINISH_LINE: has_finish = True
                if cell & Cell.CHECKPOINT: has_checkpoint = True

        missing = []
        if start_count == 0: missing.append("Start Line (🏁)")
        if not has_finish: missing.append("Finish Line (🚩)")
        if not has_checkpoint: missing.append("Checkpoint (⭐)")

        if missing:
            messagebox.showerror("Validation Error", f"Cannot save! The circuit is missing:\n" + "\n".join(missing))
            return

        if start_count < 2:
            messagebox.showwarning(
                "Validation Warning",
                f"Warning: You only have {start_count} START_LINE cell(s)!\n"
                "The game requires at least 2 to spawn players properly.\n\n"
                "Saving as a Work-in-Progress."
            )
            if name.find(" (WIP)") == -1:
                name += " (WIP)"
            else:
                logger.debug("Circuit is already a work-in-progress, skipping the tagging process")

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

    def _handle_load(self) -> None:
        """
        Fetch a selected circuit profile from the database and populate the workspace.
        """
        name = self.selected_circuit.get()
        if not name:
            return
            
        grid = dao.get_by_name(name)
        if grid:
            self._render_grid(grid)
            self.save_name_var.set(name) # populate save box with loaded name

    def _handle_delete(self) -> None:
        """
        Delete a selected circuit profile from the database.
        """
        name = self.selected_circuit.get()
        if not name:
            return
            
        try:
            dao.delete_circuit(name)
        except ValueError:
            messagebox.showerror("Error", f"Failed to delete the circuit: {name}\n\nPlease report this issue.")

        self._refresh_dropdown()

        rows, columns = int(self.rows_var.get()), int(self.cols_var.get())
        if rows < 5:
            self.rows_var.set("5")
            rows = 5
        if columns < 5:
            self.cols_var.set("5")
            columns = 5
        self._init_blank_grid(rows, columns)

    def _refresh_dropdown(self) -> None:
        """
        Query storage repositories to rebuild the drop-down circuit selection index.
        """
        circuits = list(dao.get_all().keys())
        self.dropdown['values'] = circuits
        if circuits:
            self.dropdown.set(circuits[0])