import pytest
from cubee.cells import Cell
from cubee.actions import Action
from cubee.colors import Color
from cubee.player import *
from cubee.model import Board, GameModel

def test_initialization():
    board = Board(5, 5)
    model = GameModel(
        board,
        Player("player1", Color.BLUE),
        Player("player2", Color.GREEN)
    )
    assert len(model.players) == 2

def test_assign_initial_positions():
    board = Board(5, 5)
    model = GameModel(
        board,
        Player("player1", Color.BLUE),
        Player("player2", Color.GREEN)
    )
    assert len(set(player.position for player in model.players)) == 2
    positions = [
        (0, 0),
        (0, self.board.columns-1),
        (self.board.rows-1, 0),
        (self.board.rows-1, self.board.columns-1)
    ]
    for player in model.players:
        exists = player.position in positions
        assert exists
        if exists: positions.remove(player.position)

def test_assign_cell_identities():
    board = Board(5, 5)
    players = [
        Player("player1", Color.BLUE),
        Player("player2", Color.GREEN),
        Player("player3", Color.GREEN),
        Player("player4", Color.GREEN)
    ]
    model = GameModel(board, *players)
    for i in range(len(players)):
        assert model.cell_to_player.get(players[i].cell, None) == players[i]

def test_assign_position():
    board = Board(5, 5)
    player1 = Player("player1", Color.BLUE)
    player2 = Player("player2", Color.GREEN)
    model = GameModel(board, player1, player2)
    model.assign_position(player1, (2, 2))
    
    assert player1.position == (2, 2)
    with pytest.raises(IndexError):
        model.assign_position(player2, (5, 10))

def test_get_opponents():
    board = Board(5, 5)
    players = [
        Player("player1", Color.BLUE),
        Player("player2", Color.GREEN),
        Player("player3", Color.GREEN),
        Player("player4", Color.GREEN)
    ]
    model = GameModel(board, *players)
    players.remove(model.current_player())
    assert model.get_opponents() == players
