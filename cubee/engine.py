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

    def get_initial_state(self) -> dict:
        """
        Retrieve the initial state of the game for GUI/CLI setup.

        Returns:
            dict: Contains board dimensions, list of players, and the current active player.
        """
        return {
            "board_rows": self.model.board.rows,
            "board_columns": self.model.board.columns,
            "players": self.model.players,
            "current_player": self.model.current_player()#,
            #"cells_counter": self.model.board.count_cells()
        }

    def _is_valid_position(self, row: int, column: int) -> bool:
        """
        Check if a given board position is valid for the current player to move to.

        Args:
            row (int): Row index of the target position.
            column (int): Column index of the target position.

        Returns:
            bool: True if the move is within bounds, not on opponent territory,
                and adjacent to current position.
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
        """_summary_
        
        Returns:
            list[Action]: _description_
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
        Process a move for the current player to a specific board position.

        Args:
            row (int): Target row.
            column (int): Target column.

        Returns:
            dict: Move result containing success status,
                player info, old position, modified cells, and next player.
        """
        if not self._is_valid_position(row, column):
            logger.debug(f"Move to ({row}, {column}) rejected")
            return {"success": False}
        
        current_player = self.model.current_player()
        original_position = current_player.position
        original_cell = self.model.board[row, column]

        logger.debug(f"{current_player.name} moves from {original_position} to ({row}, {column})")
        self.model.assign_position(current_player, (row, column))
        
        return {
            "success": True,
            "player": current_player,
            "old_position": original_position,
            "enclosure_modified_cells": self._post_move_updates(original_position, original_cell),
            "next_player": self.model.current_player()
        }
    
    def process_move(self, action_taken: Action) -> dict:
        """
        Process a move for the current player based on an Action (usually CLI or AI input).

        Args:
            action_taken (Action): The action to perform (UP, DOWN, LEFT, RIGHT).

        Returns:
            dict: Result of the move, similar to `process_move_to_position`.
        """
        current_player = self.model.current_player()

        # Relative position
        delta_row, delta_column = action_taken.delta
        row = current_player.row + delta_row
        column = current_player.column + delta_column

        return self.process_move_to_position(row, column)

    def _post_move_updates(self, original_position: tuple[int, int], original_cell: Cell) -> list[tuple[int, int]]:
        """
        Handle post-move updates: check for enclosures, update captured cells, and switch to the next player.

        Args:
            original_position (tuple[int, int]): The player's previous position.
            original_cell (Cell): The cell type that was originally at the destination.

        Returns:
            list[tuple[int, int]]: List of cells captured due to enclosure.
        """
        enclosure_modified_cells = []
        if self._check_enclosure(
            excluded_position = original_position,
            position = self.model.current_player().position,
            original_cell = original_cell
        ):
            logger.debug("Enclosure detected, running BFS")
            enclosure_modified_cells = self._enclosure()
        
        self._next_player()
        return enclosure_modified_cells

    def _check_enclosure(self, excluded_position: tuple[int, int], position: tuple[int, int], original_cell: Cell) -> bool:
        """
        Preliminary check to determine if the current move might have formed an enclosure.

        Args:
            excluded_position (tuple[int, int]): The previous position of the player (to ignore in checks).
            position (tuple[int, int]): Current player position.
            original_cell (Cell): The type of the cell the player moved from.

        Returns:
            bool: True if an enclosure might have occurred, False otherwise.
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
        Perform BFS to identify all empty cells that are enclosed by the current player and unreachable by opponents.

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

    def _next_player(self) -> None:
        """
        Advance the turn to the next player in the game model.
        """
        if len(self.model.players) == 0:
            logger.critical("No players available when trying to switch turns")
            raise ZeroDivisionError("There are no players available in self.model.players")

        self.model.current_player_index = (
            self.model.current_player_index + 1
        ) % len(self.model.players)

        logger.debug(f"Next player: {self.model.current_player().name}")

    def is_game_over(self) -> bool:
        """
        Check if the game is over (i.e., no empty cells remain).

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
        Compute the competitive results after the game ends.

        Returns:
            dict: Contains:
                - 'winner': Player with the most cells.
                - 'losers': Players with fewer cells, in ascending order.
                - 'cells_counter': Mapping of Cell -> number of occurrences on the board.
        """
        
        if not self.is_game_over():
            logger.warning("Requested competitive data before game ended")

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
        Reset the game state by resetting the model to its initial configuration.
        """
        logger.info("Resetting game state")
        self.model.reset()

    #AI reward computing
    def compute_reward(self,old_nb_cells: int, new_nb_cells: int, action: Action, response):
        reward = new_nb_cells - old_nb_cells

        # Enclosure bonuses
        board_size = self.model.board.columns * self.model.board.rows
        ratio = (new_nb_cells - old_nb_cells) / board_size
        enclosure_reward_value = int(50 * ratio) # For natural scaling instead of random numbers

        if len(response["enclosure_modified_cells"]) > 0:
            reward += enclosure_reward_value

        # End-game bonuses
        if self.is_game_over():
            winner = self.get_competitive_data()['winner']

            if winner == response['player']:
                reward += 10
            else:
                reward -= 10

        return reward