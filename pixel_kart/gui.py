import tkinter as tk
from tkinter import ttk, messagebox
from pixel_kart.model import Circuit
from pixel_kart.player import RandomAIPlayer
from pixel_kart.engine import RaceEngine
from pixel_kart.pixelKart_circuitFrames import CircuitRaceFrame
from pixel_kart.pixelKart_circuit_editor import CircuitEditor
import pixel_kart.pixelKart_dao as dao

class PixelKartGUI(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.circuit = None
        self.engine = None
        self.human_name = "Human"
        self.ai_player = RandomAIPlayer("Random AI")
        self.current_action = None

        self.init_ui()
        self.load_circuit("Basic")

    def init_ui(self):
        # Top bar
        top = ttk.Frame(self)
        top.pack(fill="x", pady=5)

        ttk.Button(top, text="Choose/Edit Circuit", command=self.open_editor).pack(side="left", padx=5)
        ttk.Button(top, text="New Race", command=self.new_race).pack(side="left", padx=5)

        self.info_label = ttk.Label(top, text="", font=("Arial", 10))
        self.info_label.pack(side="right", padx=10)

        # Circuit grid
        self.race_frame = CircuitRaceFrame(self)
        self.race_frame.pack(pady=10, fill="both", expand=True)

        # Action buttons
        action_frame = ttk.LabelFrame(self, text="Actions")
        action_frame.pack(fill="x", pady=8)

        actions = [
            ("Accelerate", "acc"),
            ("Brake", "brake"),
            ("Turn Left", "left"),
            ("Turn Right", "right"),
            ("Nothing", "nothing")
        ]
        for text, act in actions:
            btn = ttk.Button(action_frame, text=text,
                             command=lambda a=act: self.execute_action(a))
            btn.pack(side="left", expand=True, fill="x", padx=3)

    def open_editor(self):
        def on_chose(name):
            self.load_circuit(name)
        editor = CircuitEditor(self.parent, callback=on_chose)

    def load_circuit(self, name: str):
        dto = dao.get_by_name(name)
        if not dto:
            messagebox.showerror("Error", f"Circuit '{name}' not found")
            return
        self.circuit = Circuit(dto, name)
        self.race_frame.dto_to_grid(dto)
        self.new_race()

    def new_race(self):
        if not self.circuit:
            return
        self.engine = RaceEngine(self.circuit, required_laps=3)
        self.engine.add_kart(self.human_name, color="red")
        self.engine.add_kart(self.ai_player.name, color="blue")
        self.update_view()

    def execute_action(self, action: str):
        """Called when any action button is clicked -> execute immediately"""
        if not self.engine:
            return

        # Human plays
        self.engine.apply_action(self.human_name, action)

        # AI plays
        ai_kart = self.engine.karts[self.ai_player.name]
        ai_action = self.ai_player.choose_action(ai_kart, self.circuit)
        self.engine.apply_action(self.ai_player.name, ai_action)

        # Advance the simulation
        self.engine.step()
        self.update_view()

        # Check if race is over
        if self.engine.is_race_over():
            self.show_results()
            self.new_race()

    def update_view(self):
        karts_dict = {}
        for name, kart in self.engine.karts.items():
            if not kart.crashed:
                karts_dict[kart.pos] = kart.color
        self.race_frame.update_view(karts_dict)

        status = f"Turn: {self.engine.turn} | {self.circuit.name} | "
        for name, k in self.engine.karts.items():
            status += f"{name}: Lap {k.laps_completed}/3  Speed:{k.speed}  "
        self.info_label.config(text=status)

    def show_results(self):
        msg = "Race Over!\n\n"
        for name, kart in self.engine.karts.items():
            status = "CRASHED" if kart.crashed else f"Completed {kart.laps_completed} laps"
            msg += f"{name}: {status}\n"
        messagebox.showinfo("PixelKart Results", msg)