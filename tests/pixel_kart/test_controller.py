import pytest
from unittest.mock import MagicMock

from pixel_kart.controller import GameController
from pixel_kart.player import Human, AI, Player
from pixel_kart.actions import Action
from pixel_kart.colors import Color

# === FIXTURE ===
# This runs automatically before any test that requests it.
# It returns a clean, fresh instance of the controller and all its mocks.
@pytest.fixture
def setup_controller():
    # Mock the GUI to prevent actual Tkinter windows from spawning
    mock_gui = MagicMock()
    mock_gui.parent = MagicMock()
    
    # Mock the GameEngine
    mock_engine = MagicMock()
    
    # Create dummy players
    Player.clear_used_names()
    Player.clear_used_colors()
    human = Human(name="Player1", color=Color.BLUE)
    bot = Player(name="Bot", color=Color.ORANGE)
    
    # Create a default dummy game state
    dummy_state = {
        "board": MagicMock(),
        "current_player": human,
        "opponents": [bot],
        "laps_completed": {human: 0, bot: 0},
        "is_game_over": False
    }
    mock_engine.get_game_state.return_value = dummy_state
    
    # Initialize the Controller
    controller = GameController(engine=mock_engine, gui=mock_gui)

    # Yield all the pieces so our individual tests can manipulate them
    return controller, mock_engine, mock_gui, dummy_state, human, bot

# === TESTS ===

def test_run_gui_mode_initialization(setup_controller):
    """Test if the GUI correctly draws the initial board and binds keys."""
    # Unpack the fixture
    controller, mock_engine, mock_gui, dummy_state, _, _ = setup_controller
    
    controller.run()
    
    # Verify the board was sent to the GUI
    mock_gui.create_board.assert_called_once_with(dummy_state["board"].grid)
    
    # Verify keys were bound
    mock_gui.bind_keys.assert_called_once_with(controller._on_keypress)
    
    # Verify initial HUD and kart update
    mock_gui.update_karts.assert_called_once()
    mock_gui.update_hud.assert_called_once()

def test_keypress_human_turn(setup_controller):
    """Test that a valid human keypress correctly calls the engine."""
    controller, mock_engine, mock_gui, _, _, _ = setup_controller
    
    # Create a mock Tkinter key event for the 'w' key
    mock_event = MagicMock()
    mock_event.keysym = 'w'
    
    controller._on_keypress(mock_event)
    
    # 'w' maps to Action.ACCELERATE. Verify the engine processed it.
    mock_engine.process_move.assert_called_once_with(Action.ACCELERATE)
    
    # Verify GUI was updated after the move
    mock_gui.update_karts.assert_called_once()

def test_gui_lock_during_bot_turn(setup_controller):
    """Test that keypresses are ignored while the bot is taking its turn."""
    controller, mock_engine, _, dummy_state, _, bot = setup_controller
    
    # Change state so it's the bot's turn
    dummy_state["current_player"] = bot
    
    # Trigger the run method, which should recognize the bot and lock the GUI
    controller.run()
    
    assert controller.gui_locked is True
    
    # Try to press a key while locked
    mock_event = MagicMock()
    mock_event.keysym = 'w'
    controller._on_keypress(mock_event)
    
    # process_move should only have been called ONCE (by the bot during init), NOT by the human's keypress
    assert mock_engine.process_move.call_count == 1

def test_automated_turn_loop(setup_controller):
    """Test if the controller properly schedules the next bot turn."""
    controller, mock_engine, mock_gui, dummy_state, _, bot = setup_controller
    
    dummy_state["current_player"] = bot
    mock_engine.process_move.return_value = {"success": True}
    
    # Run a single automated turn, acting like a GUI event triggered it
    controller._handle_automated_turn(gui_event=True)
    
    # Because the game isn't over and it's still a bot's turn, 
    # it should schedule the next loop via Tkinter's `after()` method
    mock_gui.parent.after.assert_called_once()

def test_game_over_trigger(setup_controller):
    """Test if the controller properly displays the end screen when a move ends the game."""
    controller, mock_engine, mock_gui, dummy_state, human, bot = setup_controller
    
    # Simulate a keypress that ends the game
    mock_event = MagicMock()
    mock_event.keysym = 'w'
    
    # Override the state so the engine declares the game is over
    game_over_state = dict(dummy_state)
    game_over_state["is_game_over"] = True
    mock_engine.get_game_state.return_value = game_over_state
    
    # Provide a dummy leaderboard
    mock_engine.get_leaderboard.return_value = {"winner": human, "losers": [bot]}
    
    controller._on_keypress(mock_event)
    
    # Verify the end_game GUI method was called
    mock_gui.end_game.assert_called_once()
    mock_gui.update_turn_message.assert_called_with("Game over! Player1 wins!")