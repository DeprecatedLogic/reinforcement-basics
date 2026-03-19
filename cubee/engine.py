from cubee.player import Player
from cubee.model import GameModel
from cubee.actions import Action
from cubee.cells import Cell
DEBUG = True # temporary

class GameEngine:
    """
    Implements the rules and flow of the game.
    Validates moves, updates the board through the model, triggers enclosure detection when required,
        switches turns, and determines game outcome.
    (Contains no UI logic.)
    """
    
    def __init__(self, model: GameModel):
        self.model = model

    def get_initial_state(self):
        return {
            "board_rows": self.model.board.rows,
            "board_columns": self.model.board.columns,
            "players": self.model.players,
            "current_player": self.model.current_player()
        }

    def _is_valid_position(self, row: int, column: int) -> bool:
        """_summary_

        Args:
            row (int): _description_
            column (int): _description_

        Returns:
            bool: _description_
        """ 
        board = self.model.board

        # Check if we're moving out of bounds or onto opponent territory
        if not board.is_within_bounds(row, column):
            if DEBUG:
                print(f"[GameEngine._is_valid_action] Position ({row}, {column}) is out of bounds")
            return False
        if board[row, column] in (opponent.cell for opponent in self.model.get_opponents()):
            if DEBUG:
                print(f"[GameEngine._is_valid_action] Position ({row}, {column}) is invalid, cannot move onto opponent's territory")
            return False

        player = self.model.current_player()
        diff_row, diff_column = row - player.row, column - player.column
        if (diff_row, diff_column) not in Action.all_deltas:
            if DEBUG:
                print(f"[GameEngine._is_valid_action] Position ({row}, {column}) is invalid")
            return False
        
        return True
        
    def process_move_to_position(self, row: int, column: int) -> dict:
        """
        process_move description
        """
        if not self._is_valid_position(row, column):
            return {"success": False}
        
        current_player = self.model.current_player()
        original_position = current_player.position
        original_cell = self.model.board[row, column]

        position = (row, column)
        self.model.assign_position(current_player, position)
        
        return {
            "success": True,
            "player": current_player,
            "old_position": original_position,
            "enclosure_modified_cells": self._post_move_updates(original_position, original_cell),
            "next_player": self.model.current_player()
        }
    
    def process_move(self, action_taken: Action) -> dict:
        """Move current player according to an action (CLI/AI input).
        
        Args:
            action_taken (Action): _description_

        Returns:
            dict: _description_
        """
        current_player = self.mode.current_player()

        # Relative position
        delta_row, delta_column = action_taken
        row = current_player.row + delta_row
        column = current_player.column + delta_column

        return self.process_move_to_position(row, column)

    def _post_move_updates(self, original_position: tuple[int, int], original_cell: Cell) -> list[tuple[int, int]]:
        """Check enclosure, execute BFS if needed, give turn to next player.

        Args:
            original_position (tuple[int, int]): _description_
            original_cell (Cell): _description_

        Returns:
            enclosure_modified_cells (list[tuple[int, int]]): _description_
        """
        enclosure_modified_cells = []
        if self._check_enclosure(
            excluded_position = original_position,
            position = self.model.current_player().position,
            original_cell = original_cell
        ):
            enclosure_modified_cells = self._enclosure()
        
        self.next_player()
        return enclosure_modified_cells

    def _check_enclosure(self, excluded_position: tuple[int, int], position: tuple[int, int], original_cell: Cell) -> bool:
        # WARNING: Keep in mind that the 1st pre-check works BECAUSE the rules
        #   state that players CANNOT move onto opponent territory.
        #   This function is highly dependent on the game's rules and should be adapted.
        
        row, column = position
        neighbor_cells = self.model.board.get_neighbors(row, column)
        
        # Don't take into account the cell where the player came from
        neighbor_cells.remove(excluded_position)
        
        # Pre-check 1: did the player move into an empty cell?
        #   if not, skip enclosure check
        if original_cell != Cell.EMPTY:
            return False

        # Pre-check 2: are all neighboring cells (except where we came from) empty?
        #   if yes, skip enclosure check
        if all(cell == Cell.EMPTY for cell in neighbor_cells):
            return False
        
        # If the above checks failed to return False, we return True
        # NOTE: temporarily False for debugging
        return False #True

    def _enclosure(self) -> list[tuple[int, int]]:
        """
        Returns the list of EMPTY cells that should now belong to the current player
        because no opponent can reach them anymore (they are fully enclosed
        by the current player's pieces and/or board edges).
        
        Does NOT modify the board.
        """
        board = self.model.board
        current_player_color = self.model.current_player().cell
        
        # Get all opponents colors
        opponent_colors = set()
        for opponent in self.model.get_opponents():
            if opponent.cell is not None:
                opponent_colors.add(opponent.cell)

        # Error handling (no opponents present)
        if not opponent_colors:
            return []

        visited = set()
        captured_cells = []  #list to return

        # We need queue? Zzzz
        from collections import deque

        for row in range(board.rows):
            for column in range(board.columns):
                current_position = (row, column)

                # Skip if we already visited or it is not empty
                if board[current_position] != Cell.EMPTY:
                    continue
                if current_position in visited:
                    continue

                # Found start of new connected area
                cells_in_this_region = []
                bordering_player_colors = set()

                queue = deque([current_position])
                visited.add(current_position)

                while queue:
                    current_row, current_column = queue.popleft()
                    cells_in_this_region.append((current_row, current_column))

                    # Check all four possible neighbors
                    for delta_row, delta_column in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        neighbor_row = current_row + delta_row
                        neighbor_column = current_column + delta_column

                        # Outside the board, edge helps enclosure, so skip
                        if not board.is_within_bounds(neighbor_row, neighbor_column):
                            continue

                        neighbor_position = (neighbor_row, neighbor_column)
                        neighbor_value = board[neighbor_position]

                        if neighbor_value == Cell.EMPTY:
                            # Still empty, continue exploring this region
                            if neighbor_position not in visited:
                                visited.add(neighbor_position)
                                queue.append(neighbor_position)
                        else:
                            # Found a player's cell next to us, remember which player
                            bordering_player_colors.add(neighbor_value)

                # After exploring the whole connected empty area:
                # If NO opponent color borders this region → it is captured
                opponents_touching = bordering_player_colors & opponent_colors
                if len(opponents_touching) == 0:
                    captured_cells.extend(cells_in_this_region)

        return captured_cells

    def next_player(self) -> None:
        """Set the next player index."""
        if len(self.model.players) == 0:
            raise ZeroDivisionError("There are no players available in self.model.players")

        self.model.current_player_index = (self.model.current_player_index + 1) % len(self.model.players)    

    def is_game_over(self) -> bool:
        """ is_game_over description """
        cell_counter = self.model.board.count_cells()
        return cell_counter[Cell.EMPTY] == 0

    def get_competitive_data(self) -> dict:
        """Return a dictionary containing the winning player, losers, and the cells counter.
        
        Returns:
            winner: Player with the most cells.
            losers: Players with less cells, descending order.
            cells_counter: The number of cells each player has (empty cells included).
        """
        
        if not self.is_game_over():
            if DEBUG:
                print("[GameEngine.get_game_over_data] The game has NOT ended yet")

        cells_counter = self.model.board.count_cells()
        
        player_cells_counter = cells_counter.copy()
        player_cells_counter.pop(Cell.EMPTY, None)
        ranking = sorted(player_cells_counter.items(), key=lambda item: item[1])

        winner = self.model.cell_to_player[ranking[-1][0]]
        losers = [
            self.model.cell_to_player[cell]
            for cell, _ in ranking[:-1]
            if cell in self.model.cell_to_player.keys()
        ]

        return {
            "winner": winner,
            "losers": losers,
            "cells_counter": cells_counter
        }
        
    def reset_game_state(self) -> None:
        self.model.reset()