from dataclasses import dataclass
from typing import Tuple, List, Dict
from pixel_kart import const

Direction = Tuple[int, int]
Pos = Tuple[int, int]

DIRECTIONS: Dict[str, Direction] = {
    "N": (-1, 0), "S": (1, 0), "E": (0, 1), "W": (0, -1)
}
DIR_ORDER = ["N", "E", "S", "W"]  # for left/right turns

@dataclass
class Kart:
    pos: Pos
    direction: str
    speed: int = 0
    color: str = "red"
    laps_completed: int = 0
    crashed: bool = False

class Circuit:
    def __init__(self, dto: str, name: str = "Unnamed"):
        self.name = name
        self.grid: List[List[str]] = []
        self.finish_positions: set[Pos] = set()
        self._parse_dto(dto)

    def _parse_dto(self, dto: str):
        rows = dto.split(",")
        for r, row in enumerate(rows):
            self.grid.append([])
            for c, char in enumerate(row):
                t = next((k for k, v in const.PIXEL_TYPES.items() if v["letter"] == char), "ROAD")
                self.grid[r].append(t)
                if t == "FINISH":
                    self.finish_positions.add((r, c))

    def get_type(self, pos: Pos) -> str:
        r, c = pos
        if not (0 <= r < len(self.grid) and 0 <= c < len(self.grid[0])):
            return "WALL"
        return self.grid[r][c]

    def is_finish(self, pos: Pos) -> bool:
        return pos in self.finish_positions