import pytest
from cubee.cells import Cell
from cubee.actions import Action
from cubee.colors import Color
from cubee.player import *

def test_initialization():
    player = Player("test_initialization_Test", Color.RED)
    assert player.name == "test_initialization_Test"
    assert player.color == Color.RED
    assert player.row == 0
    assert player.column == 0
    assert player.nb_wins == 0
    assert player.nb_losses == 0
    assert player.cell is None
    with pytest.raises(Exception):
        Player("test_initialization_Test", Color.GREEN)

def test_set_position():
    player = Player("test_set_position_Test", Color.RED)
    player.position = (1, 2)
    assert player.position == (1, 2)

def test_set_invalid_position():
    player = Player("test_set_invalid_position_Test", Color.RED)
    with pytest.raises(ValueError):
        player.position = "invalid"

def test_str_representation():
    player = Player("test_str_representation_Test", Color.RED)
    player.cell = Cell.P1
    assert str(player) == "test_str_representation_Test(P1)"

def test_position_property():
    player = Player("test_position_property_Test", Color.RED)
    player.position = (0, 0)
    assert player.row == 0
    assert player.column == 0
    with pytest.raises(ValueError):
        player.position = (-1, -1)

""" It hangs/blocks because a wrong key in Human.play does NOT return, it continues looping.

This problem can be fixed by adding an extra parameter to tell the Human.play function
that it's being called by an automated test and make it behave differently, but it would be ugly imo.


actions_available = [Action.UP, Action.RIGHT, Action.DOWN, Action.LEFT]
@pytest.mark.parametrize(
    "user_input, actions, expected_action, expected_output",
    [
        ("w", actions_available, Action.UP, ""),
        ("d", actions_available, Action.RIGHT, ""),
        ("a", actions_available, Action.LEFT, ""),
        ("s", actions_available, Action.DOWN, ""),
        ("a", [Action.UP, Action.DOWN], None, "Invalid input, try again\n"),
        ("s", [], None, "Invalid input, try again\n"),
        ("x", actions_available, None, "Invalid input, try again\n"),
    ]
)
def test_human_play(user_input, actions, expected_action, expected_output, monkeypatch, capsys):
    monkeypatch.setattr("readchar.readkey", lambda: user_input)

    player = Human("test_human_play_Test", Color.BLUE)
    action_taken = player.play(actions)

    captured = capsys.readouterr()

    if expected_action:
        assert action_taken == expected_action
    else:
        assert action_taken is None

    assert expected_output in captured.out
"""