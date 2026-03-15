import pytest
from cubee.cells import Cell
from cubee.model import Board

def test_initialization():
    board = Board(5, 10)
    assert board.rows == 5
    assert board.columns == 10
    board = Board(20, 20)
    assert board.rows == 20
    assert board.columns == 20

def test_invalid_rows():
    with pytest.raises(ValueError) as exc_info:
        Board(0, 5)

    assert "Rows value should be bigger than 0!" in str(exc_info.value)

def test_invalid_columns():
    with pytest.raises(ValueError) as exc_info:
        Board(5, 0)

    assert "Columns value should be bigger than 0!" in str(exc_info.value)

def test_size():
    board = Board(10, 5)
    assert board.size == (10, 5)

    board.size = (5, 10)
    assert board.size == (5, 10)

def test_get_neighbors():
    board = Board(5, 5)
    neighbors_2 = board.get_neighbors(0, 0)
    neighbors_4 = board.get_neighbors(2, 2)

    assert len(neighbors_2) == 2
    assert len(neighbors_4) == 4

# TODO: maybe remove this test
def test_getitem_setitem():
    board = Board(5, 5)
    assert board[2, 2] == Cell.EMPTY

    board[2, 2] = Cell.P1
    assert board[2, 2] == Cell.P1

def test_count_cells():
    board = Board(5, 5)
    board.grid[0][0] = Cell.P1
    board.grid[0][1] = Cell.P1
    board.grid[1][0] = Cell.P1
    board.grid[2][2] = Cell.P2
    board.grid[3][4] = Cell.P4
    board.grid[4][0] = Cell.P4
    counter = board.count_cells()

    assert counter[Cell.EMPTY] == 19
    assert counter[Cell.P1] == 3
    assert counter[Cell.P2] == 1
    assert counter[Cell.P3] == 0
    assert counter[Cell.P4] == 2

@pytest.mark.parametrize("row, column, expected", [
    (0, 0, True),
    (2, 2, True),
    (4, 4, True),
    (0, 4, True),
    (-1, -1, False),
    (-1, 1, False),
    (5, 5, False),
    (5, 2, False),
    (2, 5, False)
])
def test_is_within_bounds(row, column, expected):
    board = Board(5, 5)
    assert board.is_within_bounds(row, column) == expected

def test_str_representation():
    board = Board(2, 3)
    expected_str = "\n".join((
        "-------------",
        "| 0 | 0 | 0 |",
        "-------------",
        "| 0 | 0 | 0 |",
        "-------------"
    ))
    assert str(board) == expected_str

def test_reset():
    board = Board(4, 4)
    board[1,2] = Cell.P2
    board.enclosure_modified_cells = [(0,0), (3,3)]
    board.reset()
    assert all(c == Cell.EMPTY for row in board.grid for c in row)
    assert board.enclosure_modified_cells == []
