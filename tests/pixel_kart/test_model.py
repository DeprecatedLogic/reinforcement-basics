import pytest
from pixel_kart.model import Board, GameModel
from pixel_kart.player import Player
from pixel_kart.cells import Cell, CELL_TO_COLOR
from pixel_kart.colors import Color 

def test_player_duplicate_name_exception():
    """Test that creating two players with the same name raises an Exception."""
    Player.clear_used_names()
    Player.clear_used_colors()
    
    # Create the first player (should work)
    Player(name="Test", color=Color.RED)
    
    # Attempt to create a clone
    with pytest.raises(Exception, match="already in use"):
        Player(name="Test", color=Color.BLUE)

def test_player_duplicate_color_exception():
    """Test that creating two players with the same color raises an Exception."""
    Player.clear_used_names()
    Player.clear_used_colors()
    
    # Create the first player (should work)
    Player(name="P1", color=Color.RED)
    
    # Attempt to create a clone
    with pytest.raises(Exception, match="already in use"):
        Player(name="P2", color=Color.RED)

#def test_player_environment_color_exception():
#    """Test that picking a color matching the environment raises a ValueError."""
#    Player.clear_used_names()
#    Player.clear_used_colors()
#
#    # Grab whatever color is mapped to the first environment cell type
#    env_color = list(CELL_TO_COLOR.values())[0]
#    
#    # Attempt to camouflage the player
#    with pytest.raises(ValueError, match="environment"):
#        Player(name="Test", color=env_color)

def test_model_overcrowding_exception():
    """Test that the Model raises an Exception if players outnumber start lines."""
    Player.clear_used_names()
    Player.clear_used_colors()

    board = Board(rows=3, columns=3)
    # Give the board exactly ONE start line cell
    board.start_line.add((1, 1))
    
    player1 = Player(name="P1", color=Color.RED)
    player2 = Player(name="P2", color=Color.BLUE)
    
    # Attempt to initialize a game with 2 players but only 1 spawn point
    with pytest.raises(Exception, match="Too many players"):
        GameModel(board, player1, player2)


def test_model_initial_assignment():
    """Test that players are correctly assigned to start lines and initial states are set."""
    Player.clear_used_names()
    Player.clear_used_colors()
    
    board = Board(rows=5, columns=5)
    # Give the board exactly TWO start line cells
    board.start_line.add((2, 2))
    board.start_line.add((2, 3))
    
    player1 = Player(name="P1", color=Color.RED)
    player2 = Player(name="P2", color=Color.BLUE)
    
    # This should succeed and trigger _assign_initial_positions automatically
    model = GameModel(board, player1, player2, laps_required=3)
    
    # Assert both players are sitting on valid start lines
    assert player1.position in {(2, 2), (2, 3)}
    assert player2.position in {(2, 2), (2, 3)}
    
    # Assert they didn't spawn on top of each other
    assert player1.position != player2.position
    
    # Assert the laps dictionary was initialized correctly
    assert model.laps_completed[player1] == 0
    assert model.laps_completed[player2] == 0
    
    # Assert player attributes were reset/initialized
    assert player1.start_line is True
    assert player1.speed == 0