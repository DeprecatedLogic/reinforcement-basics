from cubee.player import Player
from cubee.model import GameModel
from cubee.actions import Action, ACTION_DELTAS
from cubee.cells import Cell
import logging
logger = logging.getLogger(__name__)

class GameEngine:
    """
    Encapsulates the game logic and rules.  
    
    Validates moves, updates the game model, detects enclosures,
    switches turns, and determines the game outcome.  
    Contains no UI logic.
    """
    
    def __init__(self, model: GameModel) -> None:
        """
        Initialize the game engine with a game model.

        Args:
            model (GameModel): The game model containing board, players, and game state.
        """
        self.model = model

    def get_game_state(self) -> dict:
        """
        Build and return a snapshot of the current game state.
        
        Includes board dimensions, current player, opponents, next player index,
        and valid actions for the current turn.

        Returns:
            dict: Game state representation for controller/AI usage.
        """
        return {
            "board_grid": self.model.board.grid,
            "board_rows": self.model.board.rows,
            "board_columns": self.model.board.columns,
            "current_player": self.model.current_player(),
            "opponents": self.model.get_opponents(),
            "next_player": self.next_player(apply=False),
            "valid_actions": self.get_valid_actions(),
            #"player_cell_positions" : self.model.player_cell_positions,
            #"is_game_over": self.is_game_over()
        }

    def _is_valid_position(self, row: int, column: int) -> bool:
        """
        Determine whether a target position is a legal move.

        A position is valid if it is within bounds, not occupied by an opponent,
        and reachable via a single-step action from the current player's position.

        Args:
            row (int): Target row index.
            column (int): Target column index.

        Returns:
            bool: True if the position is valid, False otherwise.
        """
        board = self.model.board

        # Check if we're moving out of bounds or onto opponent territory
        if not board.is_within_bounds(row, column):
            logger.debug(f"Position ({row}, {column}) is out of bounds")
            return False
        if board[row, column] in (opponent.cell for opponent in self.model.get_opponents()):
            logger.debug(f"Position ({row}, {column}) is invalid, cannot move onto opponent's territory")
            return False

        player = self.model.current_player()
        diff_row, diff_column = row - player.row, column - player.column
        if (diff_row, diff_column) not in ACTION_DELTAS:
            logger.debug(f"Position ({row}, {column}) is invalid")
            return False
        
        return True
        
    def get_valid_actions(self) -> list[Action]:
        """
        Compute the list of valid actions for the current player.

        Each possible action is evaluated by checking whether the resulting
        position is within bounds, not occupied by an opponent, and adjacent
        to the player's current position.

        Returns:
            list[Action]: List of actions that the current player can legally perform.
        """
        valid_actions = []
        current_player = self.model.current_player()
        
        for action in tuple(Action):
            # Relative position
            delta_row, delta_column = action.delta
            row = current_player.row + delta_row
            column = current_player.column + delta_column
            
            if self._is_valid_position(row, column):
                valid_actions.append(action)
        
        return valid_actions

    def process_move_to_position(self, row: int, column: int) -> dict:
        """
        Execute a move to a specific board position for the current player.

        Validates the move, updates the model, applies enclosure logic, and
        advances the turn.

        Args:
            row (int): Target row.
            column (int): Target column.

        Returns:
            dict: Result of the move including success flag, updated player,
            captured cells, and game status.
        """
        if not self._is_valid_position(row, column):
            logger.debug(f"Move to ({row}, {column}) rejected")
            return {"success": False}
        
        current_player = self.model.current_player()
        original_position = current_player.position
        original_cell = self.model.board[row, column]

        logger.debug(f"{current_player.name} moves from {original_position} to ({row}, {column})")
        
        nb_cells_gained = 0
        if self.model.assign_position(current_player, (row, column)):
            nb_cells_gained += 1
        
        enclosure_modified_cells = self._post_move_updates(original_position, original_cell)
        nb_cells_gained += len(enclosure_modified_cells)

        return {
            "success": True,
            "old_player": current_player,
            "old_position": original_position,
            "enclosure_modified_cells": enclosure_modified_cells,
            "current_player": self.model.current_player(),
            "nb_cells_gained": nb_cells_gained,
            "is_game_over": self.is_game_over()
        }
    
    def process_move(self, action_taken: Action) -> dict:
        """
        Execute a move based on an action.

        Translates the action into a target position and delegates processing
        to the position-based handler.

        Args:
            action_taken (Action): Action to execute.

        Returns:
            dict: Result of the move.
        """
        current_player = self.model.current_player()

        # Relative position
        delta_row, delta_column = action_taken.delta
        row = current_player.row + delta_row
        column = current_player.column + delta_column

        return self.process_move_to_position(row, column)

    def _post_move_updates(self, original_position: tuple[int, int], original_cell: Cell) -> list[tuple[int, int]]:
        """
        Apply post-move logic including enclosure detection and turn switching.

        Args:
            original_position (tuple[int, int]): Previous player position.
            original_cell (Cell): Cell type at destination before the move.

        Returns:
            list[tuple[int, int]]: Positions of cells captured via enclosure.
        """
        enclosure_modified_cells = []
        if self._check_enclosure(
            excluded_position = original_position,
            position = self.model.current_player().position,
            original_cell = original_cell
        ):
            logger.debug("Enclosure detected, running BFS")
            enclosure_modified_cells = self._enclosure()
        
        self.next_player()
        return enclosure_modified_cells

    def _check_enclosure(self, excluded_position: tuple[int, int], position: tuple[int, int], original_cell: Cell) -> bool:
        """
        Perform a preliminary check to determine if enclosure detection is needed.

        Uses heuristic conditions based on movement and neighboring cells to
        avoid unnecessary BFS computation.

        Args:
            excluded_position (tuple[int, int]): Previous position to ignore.
            position (tuple[int, int]): Current player position.
            original_cell (Cell): Cell type at destination before the move.

        Returns:
            bool: True if enclosure detection should run, False otherwise.
        """
        # WARNING: Keep in mind that the 1st pre-check works BECAUSE the rules
        #   state that players CANNOT move onto opponent territory.
        #   This function is highly dependent on the game's rules and
        #   should be adapted each time they change.
        
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
        return True

    def _enclosure(self) -> list[tuple[int, int]]:
        """
        Identify and capture enclosed regions using BFS.

        Marks empty cells that are not reachable by any opponent as owned
        by the current player.

        Returns:
            list[tuple[int, int]]: Positions of captured cells.
        """
        board = self.model.board
        current_player = self.model.current_player()

        from collections import deque

        # Get opponent colors
        opponent_colors = {
            opponent.cell
            for opponent in self.model.get_opponents()
            if opponent.cell is not None
        }

        if not opponent_colors:
            logger.debug("No opponents found, skipping enclosure")
            return []

        reachable_by_opponent = set()
        queue = deque()

        # Seed BFS with all opponent cells because we can technically start from many nodes
        for row in range(board.rows):
            for col in range(board.columns):
                pos = (row, col)
                if board[pos] in opponent_colors:
                    queue.append(pos)
                    reachable_by_opponent.add(pos)

        # BFS expansion
        while queue:
            row, column = queue.popleft()

            for delta_r, delta_c in ACTION_DELTAS:
                neighbor_r, neighbor_c = row + delta_r, column + delta_c

                if not board.is_within_bounds(neighbor_r, neighbor_c):
                    continue

                neighbor = (neighbor_r, neighbor_c)

                # Avoid revisiting (prevent infinite loops/redundant work)
                if neighbor in reachable_by_opponent:
                    continue

                neighbor_cell = board[neighbor]

                # Opponent can move through EMPTY or their own cells
                if neighbor_cell == Cell.EMPTY or neighbor_cell in opponent_colors:
                    reachable_by_opponent.add(neighbor)
                    queue.append(neighbor)

        # Any EMPTY not reachable is enclosed
        captured_cells = []

        # Add all empty cells not reachable by opponent
        for row in range(board.rows):
            for col in range(board.columns):
                pos = (row, col)
                if board[pos] == Cell.EMPTY and pos not in reachable_by_opponent:
                    captured_cells.append(pos)
                    board[pos] = current_player.cell

        logger.debug(f"Captured {len(captured_cells)} cells via enclosure")
        return captured_cells

    def next_player(self, apply: bool = True) -> Player:
        """
        Advance or preview the next player in turn order.

        Args:
            apply (bool): If True, updates the model to the next player and returns the next player.
                If False, returns the next player without applying.

        Returns:
            Player: Next player.
        """
        if len(self.model.players) == 0:
            logger.critical("No players available when trying to switch turns")
            raise ZeroDivisionError("There are no players available in self.model.players")
        
        index = (self.model.current_player_index + 1) % len(self.model.players)
        if apply:
            self.model.current_player_index = index
            logger.debug(f"Next player: {self.model.current_player().name}")
        
        return self.model.players[index]

    def is_game_over(self) -> bool:
        """
        Check whether the game has ended.

        The game is considered over when no empty cells remain on the board.

        Returns:
            bool: True if the game is finished, False otherwise.
        """
        cell_counter = self.model.board.count_cells()

        game_over = cell_counter[Cell.EMPTY] == 0
        if game_over:
            logger.info("Game over detected")

        return game_over

    def get_competitive_data(self) -> dict:
        """
        Compute final rankings and scores for all players.

        Determines the winner based on cell counts and orders remaining players.

        Returns:
            dict: Contains  
                - 'winner': Player with the most cells.  
                - 'losers': Players with fewer cells, in ascending order.  
                - 'cells_counter': Mapping of Cell -> number of occurrences on the board.
        """
        temp_level = logger.level
        logger.setLevel(logging.WARNING)
        if not self.is_game_over():
            logger.warning("Requested competitive data before game ended")
        logger.setLevel(temp_level)

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
        """
        Reset the underlying game model to its initial state.

        Clears the board and reinitializes players and turn order.
        """
        logger.info("Resetting game state")
        self.model.reset()