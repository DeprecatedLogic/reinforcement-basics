import pytest
from cubee.cells import Cell
from cubee.actions import Action
from cubee.colors import Color
from cubee.player import *

def test_initialization():
    player = Player("Test", Color.RED)
    assert player.name == "Test"
    assert player.color == Color.RED
    assert player.row == 0
    assert player.column == 0
    assert player.nb_wins == 0
    assert player.nb_losses == 0
    assert player.cell is None
    with pytest.raises(Exception):
        Player("Test", Color.GREEN)

def test_set_position():
    player = Player("Test", Color.RED)
    player.position = (1, 2)
    assert player.position == (1, 2)

def test_set_invalid_position():
    player = Player("Test", Color.RED)
    with pytest.raises(ValueError):
        player.position = "invalid"

def test_str_representation():
    player = Player("Test", Color.RED)
    player.cell = Cell.P1
    assert str(player) == "Test(P1)"

def test_position_property():
    player = Player("Test", Color.RED)
    player.position = (0, 0)
    assert player.row == 0
    assert player.column == 0
    with pytest.raises(ValueError):
        player.position = (-1, -1)

actions_available = [Action.UP, Action.RIGHT, Action.DOWN, Action.LEFT]
@pytest.mark.parametrize(
    "user_input, actions, expected_action, expected_output",
    [
        ("UP", actions_available, Action.UP, ""),
        ("RIGHT", actions_available, Action.RIGHT, ""),
        ("LEFT", actions_available, Action.LEFT, ""),
        ("DOWN", actions_available, Action.DOWN, ""),
        ("LEFT", [Action.UP, Action.DOWN], None, "[Player.play] Invalid input, try again\n"),
        ("DOWN", [Action.RIGHT, Action.LEFT], None, "[Player.play] Invalid input, try again\n"),
        ("INVALID", actions_available, None, "[Player.play] Invalid input, try again\n"),
        ("U P", actions_available, None, "[Player.play] An uncaught error occured: "),
        ("DOWN", actions_available, Action.DOWN, ""),
        (" down ", actions_available, Action.DOWN, ""),
        ("left\n", actions_available, Action.LEFT, "")
    ]
)
def test_human_play(user_input, actions, expected_action, expected_output, monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: user_input)

    player = Human("Test", Color.BLUE)
    action_taken = player.play(actions)

    captured = capsys.readouterr()

    if expected_action:
        assert action_taken == expected_action
    else:
        assert action_taken is None

    assert expected_output in captured.out
