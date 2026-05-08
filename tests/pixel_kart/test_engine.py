import pytest
from pixel_kart.engine import GameEngine
from pixel_kart.model import GameModel, Board
from pixel_kart.player import Player
from pixel_kart.cells import Cell
from pixel_kart.actions import Action
from pixel_kart.directions import DIRECTION_ORDER
from pixel_kart.colors import Color

@pytest.fixture
def engine() -> GameEngine:
    """
    Builds a 5x5 dummy track for isolated engine testing.
    Track layout:
    - (0,0): WALL        | (0,2): CHECKPOINT
    - (2,1) & (2,2): START_LINE  | (2,3): FINISH_LINE
    - (4,2) to (4,4): GRASS
    - Everywhere else: ROAD
    """
    board = Board(rows=5, columns=5)
    grid = [[Cell.ROAD for _ in range(5)] for _ in range(5)]
    grid[0][0] = Cell.WALL
    grid[0][2] = Cell.ROAD | Cell.CHECKPOINT
    grid[2][1] = Cell.START_LINE  # Added second start line
    grid[2][2] = Cell.START_LINE
    grid[2][3] = Cell.ROAD | Cell.FINISH_LINE
    grid[4][2] = Cell.GRASS
    grid[4][3] = Cell.GRASS
    grid[4][4] = Cell.GRASS
    board.grid = grid
    
    # Populate start_line set with BOTH coordinates
    board.start_line.add((2, 1))
    board.start_line.add((2, 2))
    board.finish_line.add((2, 3))
    
    Player.clear_used_names()
    Player.clear_used_colors()

    # Create TWO dummy players to test turn switching
    player1 = Player(name="TestDummy1", color=Color.RED)
    player2 = Player(name="TestDummy2", color=Color.BLUE)
    
    model = GameModel(board, player1, player2, laps_required=3)
    
    # Reset both players to a predictable state
    for p in model.players:
        p.direction_index = 0
        p.speed = 0
        p.crashed = False
    
    return GameEngine(model)

def test_wall_crash(engine: GameEngine):
    """Test that moving into a WALL stops the kart and sets crashed to True."""
    player = engine.model.current_player()
    
    # Place player right next to the wall at (0, 0)
    # We use engine.model.assign_position so history is tracked correctly
    engine.model.assign_position(player, (0, 1))
    player.speed = 0
    player.crashed = False
    
    # Find the index for the 'West' vector (0, -1) to drive into the wall
    west_index = next(i for i, d in enumerate(DIRECTION_ORDER) if d.delta == (0, -1))
    player.direction_index = west_index
    
    # Accelerate into the wall
    result = engine.process_move(Action.ACCELERATE)
    
    assert player.crashed is True
    assert player.speed == 0
    # The kart shouldn't actually occupy the wall cell
    assert player.position == (0, 1)
    assert result["success"] is True

def test_grass_penalty_reverse(engine: GameEngine):
    """Test that reversing into GRASS correctly arrests momentum to 0."""
    player = engine.model.current_player()
    
    # Place player on ROAD, right next to the GRASS strip
    engine.model.assign_position(player, (4, 1))
    player.speed = 0
    player.crashed = False
    
    # To reverse into (4,2) which is East, we must FACE West (0, -1) 
    west_index = next(i for i, d in enumerate(DIRECTION_ORDER) if d.delta == (0, -1))
    player.direction_index = west_index
    
    # Hit BRAKE to go to speed -1 (reversing East into the grass at 4,2)
    result = engine.process_move(Action.BRAKE)
    
    # Grass penalty (int(-1 / 2)) should immediately set speed to 0
    assert player.speed == 0
    assert player.position == (4, 2)
    assert result["success"] is True

def test_multi_step_move(engine: GameEngine):
    """Test that a speed of 2 correctly moves the player exactly 2 cells."""
    player = engine.model.current_player()
    
    # Place player at top of the board with clear road ahead
    engine.model.assign_position(player, (1, 1))
    
    # Face South (1, 0)
    south_index = next(i for i, d in enumerate(DIRECTION_ORDER) if d.delta == (1, 0))
    player.direction_index = south_index
    
    # Forcibly set speed to 2 and process the move
    player.speed = 2
    engine.process_move_to_position(DIRECTION_ORDER[south_index])
    
    # Player should have moved from (1,1) -> (2,1) -> (3,1)
    assert player.position == (3, 1)
    assert player.crashed is False

def test_out_of_bounds_crash(engine: GameEngine):
    """Test that driving off the board causes a crash and stops movement."""
    player = engine.model.current_player()
    
    # Place player on the top edge
    engine.model.assign_position(player, (0, 4))
    
    # Face North (-1, 0) to drive off the board
    north_index = next(i for i, d in enumerate(DIRECTION_ORDER) if d.delta == (-1, 0))
    player.direction_index = north_index
    
    # Forcibly give speed and move
    player.speed = 1
    engine.process_move_to_position(DIRECTION_ORDER[north_index])
    
    # Should be crashed and remain at the last valid coordinate
    assert player.crashed is True
    assert player.speed == 0
    assert player.position == (0, 4)

def test_turn_switch(engine: GameEngine):
    """Test that the engine correctly switches the active player after a valid turn."""
    # Capture the player who is currently taking their turn
    first_player = engine.model.current_player()
    
    # Take an action (NOTHING maintains speed 0, meaning stationary, but still ends turn)
    engine.process_move(Action.NOTHING)
    
    # Capture the player whose turn it is now
    second_player = engine.model.current_player()
    
    # They should not be the same player
    assert first_player != second_player

def test_anti_cheat_golden_path(engine: GameEngine):
    """Test a legitimate lap: Start -> Checkpoint -> Finish."""
    player = engine.model.players[0]
    
    # 1. Spawn on Start Line (2, 2)
    engine.model.assign_position(player, (2, 2))
    engine._anti_cheat(player, (2, 2))
    assert player.start_line is True
    
    # 2. Drive to Checkpoint (0, 2)
    engine.model.assign_position(player, (0, 2))
    engine._anti_cheat(player, (0, 1))
    assert player.checkpoint is True
    
    # 3. Drive to Finish Line (2, 3)
    engine.model.assign_position(player, (2, 3))
    engine._anti_cheat(player, (2, 2))
    
    # Assert Lap Complete and keys burned!
    assert engine.model.laps_completed[player] == 1
    assert player.start_line is False
    assert player.checkpoint is False


def test_anti_cheat_wiggle_exploit(engine: GameEngine):
    """Test the Wiggle: Reversing from Start directly into Finish."""
    player = engine.model.players[0]
    
    # 1. Spawn on Start Line (2, 2)
    engine.model.assign_position(player, (2, 2))
    engine._anti_cheat(player, (2, 2))
    
    # 2. Reverse directly into Finish Line (2, 3) without Checkpoint
    engine.model.assign_position(player, (2, 3))
    is_cheating = engine._anti_cheat(player, (2, 2))
    
    # Assert Firewall Triggered: Lap denied, start flag burned!
    assert engine.model.laps_completed[player] == 0
    assert player.start_line is False
    assert player.checkpoint is False
    assert is_cheating is True


def test_anti_cheat_reverse_heist(engine: GameEngine):
    """Test the Heist: Burning the start flag, then trying to complete the lap anyway."""
    player = engine.model.players[0]
    
    # Wiggle into Finish Line (burns the start flag)
    engine.model.assign_position(player, (2, 2))
    engine._anti_cheat(player, (2, 2)) # Gets Start Flag
    engine.model.assign_position(player, (2, 3))
    engine._anti_cheat(player, (2, 2)) # Burns Start Flag
    
    # Drive all the way to Checkpoint
    engine.model.assign_position(player, (0, 2))
    engine._anti_cheat(player, (0, 1)) # Gets Checkpoint Flag
    
    # Drive back to Finish Line
    engine.model.assign_position(player, (2, 3))
    is_cheating = engine._anti_cheat(player, (2, 2))
    
    # Assert Lap Denied because they lost the Start Flag in Step 1!
    assert engine.model.laps_completed[player] == 0
    assert is_cheating is True


def test_anti_cheat_wrong_way_driver(engine: GameEngine):
    """Test driving backwards around the track: Checkpoint -> Start -> Finish."""
    player = engine.model.players[0]
    
    # Player manages to hit the Checkpoint first
    engine.model.assign_position(player, (0, 2))
    engine._anti_cheat(player, (0, 1))
    assert player.checkpoint is True
    
    # Player then drives backwards into the Start Line
    engine.model.assign_position(player, (2, 2))
    engine._anti_cheat(player, (1, 2))
    
    # Start Line logic forces checkpoint to False!
    assert player.start_line is True
    assert player.checkpoint is False
    
    # Player hits Finish Line
    engine.model.assign_position(player, (2, 3))
    is_cheating = engine._anti_cheat(player, (2, 2))
    
    # Assert Lap Denied!
    assert engine.model.laps_completed[player] == 0
    assert is_cheating is True