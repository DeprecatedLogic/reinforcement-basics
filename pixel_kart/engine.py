from pixel_kart.model import Circuit, Kart, DIRECTIONS, DIR_ORDER

class RaceEngine:
    def __init__(self, circuit: Circuit, required_laps: int = 3):
        self.circuit = circuit
        self.required_laps = required_laps
        self.karts: dict[str, Kart] = {}
        self.turn = 0

    def add_kart(self, name: str, start_pos=None, color="red"):
        if start_pos is None:
            start_pos = next(iter(self.circuit.finish_positions))
        self.karts[name] = Kart(pos=start_pos, direction="E", speed=0, color=color)

    def apply_action(self, player_name: str, action: str):
        kart = self.karts[player_name]
        if kart.crashed:
            return

        if action == 'acc':
            kart.speed = min(2, kart.speed + 1)
        elif action == 'brake':
            kart.speed = max(-1, kart.speed - 1)
        elif action == 'left':
            idx = DIR_ORDER.index(kart.direction)
            kart.direction = DIR_ORDER[(idx - 1) % 4]
        elif action == 'right':
            idx = DIR_ORDER.index(kart.direction)
            kart.direction = DIR_ORDER[(idx + 1) % 4]
        # 'nothing' does nothing

    def step(self):
        self.turn += 1
        for name, kart in self.karts.items():
            if kart.crashed:
                continue
            self._move_kart(kart)

    def _move_kart(self, kart: Kart):
        dr, dc = DIRECTIONS[kart.direction]
        speed = kart.speed
        current_type = self.circuit.get_type(kart.pos)
        if current_type == "GRASS":
            speed = speed // 2

        steps = abs(speed)
        step_dir = 1 if speed >= 0 else -1

        for _ in range(steps):
            new_pos = (kart.pos[0] + dr * step_dir, kart.pos[1] + dc * step_dir)

            cell_type = self.circuit.get_type(new_pos)
            if cell_type == "WALL":
                kart.crashed = True
                break
            if not (0 <= new_pos[0] < len(self.circuit.grid) and
                    0 <= new_pos[1] < len(self.circuit.grid[0])):
                kart.speed = 0
                break

            # Finish line logic (only Eastward crossing)
            was_on_finish = self.circuit.is_finish(kart.pos)
            now_on_finish = self.circuit.is_finish(new_pos)

            if not was_on_finish and now_on_finish and kart.direction == "E":
                kart.laps_completed += 1

            kart.pos = new_pos

    def is_race_over(self) -> bool:
        for k in self.karts.values():
            if k.crashed or k.laps_completed >= self.required_laps:
                return True

    def get_results(self):
        return {name: k.laps_completed for name, k in self.karts.items()}