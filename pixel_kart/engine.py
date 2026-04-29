from pixel_kart.player import Player
from pixel_kart.model import GameModel
from pixel_kart.actions import Action
from pixel_kart.directions import Direction, DIRECTION_DELTAS, DIRECTION_ORDER
from pixel_kart.cells import Cell
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
        
        Includes board grid, board rows and columns, current player, opponents,
        next player index, and if game is over.

        Returns:
            dict: Game state representation for controller/AI usage.
        """
        return {
            "board": self.model.board,
            "current_player": self.model.current_player(),
            "opponents": self.model.get_opponents(),
            "next_player": self.next_player(apply=False),
            "is_game_over": self.is_game_over(),
            "laps_completed": self.model.laps_completed,
            "laps_required": self.model.laps_required
        }

    def _should_crash(self, row: int, column: int) -> bool:
        """
        _summary_

        Args:
            row (int): _description_
            column (int): _description_

        Returns:
            bool: _description_
        """
        board = self.model.board
        
        # Check if we're moving out of bounds
        if not board.is_within_bounds(row, column):
            logger.debug(f"Player crashed while going out of bounds ({row}, {column})")
            return True

        # Check if we're moving onto a wall or similar object that can crash karts (add objects with `|` operator)
        crashing_objects = Cell.WALL
        cell = board[row, column]
        if cell & crashing_objects:
            logger.debug(f"Player crashed against {cell} at position ({row}, {column})")
            return True
        
        return False

    def _apply_speed_effects(self, board_cell: Cell, speed: int) -> int:
        """_summary_

        Args:
            cell (Cell): _description_
            speed (int): _description_

        Returns:
            int: _description_
        """
        if board_cell & Cell.GRASS:
            # Use `speed // 2` if going backward should be a constant -1
            speed = int(speed / 2) # drives both 1 and -1 towards 0 (slows down both directions)

        return speed

    def process_move_to_position(self, direction: Direction) -> dict:
        """
        _summary_

        Args:
            direction (Direction): _description_

        Returns:
            dict: Result of the move including success flag, old player,
            current player, and game status.
        """
        board = self.model.board
        current_player = self.model.current_player()
        position = current_player.position
        speed = current_player.speed
        steps = abs(speed)
        cell = board[position]
        is_stationary = steps == 0
        cells_encountered = []

        # Stationary
        if is_stationary:
            logger.debug(f"Player is stationary")

        else: # moving
            logger.debug(f"{current_player} moving from {position} with direction {direction.name} and speed {speed}")
            
            # Physics are calculated and applied for each step
            for step in range(steps):
                row, column = current_player.position

                # Reverse direction if speed is negative for this step
                direction_delta = direction.delta
                if speed < 0:
                    direction_index = (current_player.direction_index + 2) % 4
                    direction_delta = DIRECTION_ORDER[direction_index].delta

                # Calculate the player's new position for this step
                step_row = row + direction_delta[0]
                step_column = column + direction_delta[1]
                
                # Player crashed
                if self._should_crash(step_row, step_column):
                    logger.info(f"Player {current_player} crashed")
                    current_player.crashed = True
                    current_player.speed = 0
                    break
                else:
                    # Assign the new position to the player and get cell type
                    cell = self.model.assign_position(current_player, (step_row, step_column))
                    cells_encountered.append(cell)

                    # Apply speed effects and update the player's speed value
                    current_player.speed = speed = self._apply_speed_effects(cell, speed)
                    
                    # Run the anti-cheat (resolves all kinds of cheating + counts laps)
                    is_cheating = self._anti_cheat(current_player, original_position=position)
                    if is_cheating:
                        logger.info(f"Player {current_player} was found cheating")
                        break
        
        self.next_player()

        # Adjust the data returned based on Controller requirements
        return {
            "success": True,
            "old_player": current_player, # just in case it's needed (might remove later)
            "cells_encountered": cells_encountered, # for whatever reason...
            "current_player": self.model.current_player(),
            "is_stationary": is_stationary,
            "is_game_over": self.is_game_over()
        }

    def _anti_cheat(self, player: Player, original_position: tuple[int, int]) -> bool:
        """
        _summary_

        Args:
            player (Player): _description_
            original_position (tuple[int, int]): _description_

        Returns:
            bool: _description_
        """
        board = self.model.board
        cell = board[player.position]
        is_cheating = False

        # Check if player is moving faster than allowed
        if player.speed < -1 or player.speed > 2:
            logger.debug(f"Player {player} is moving faster than allowed\nSpeed set to 0\nPlayer sent back to original position")
            player.speed = 0
            player.position = original_position
            is_cheating = True # or a bug ? lol

        # Allow the player to complete laps in the right conditions only
        if cell & Cell.CHECKPOINT:
            player.checkpoint = True

        elif cell & Cell.START_LINE:
            player.start_line = True
            player.checkpoint = False

        elif cell & Cell.FINISH_LINE:
            if player.start_line and player.checkpoint:
                self.model.laps_completed[player] += 1
            else:
                logger.debug(f"Player {player} reached the finish line by cheating\nSkipped lap count")
                is_cheating = True

            player.start_line = False
            player.checkpoint = False

        return is_cheating

    def process_move(self, action_taken: Action) -> dict:
        """
        _summary_

        Args:
            action_taken (Action): Action to execute.

        Returns:
            dict: Result of the move.
        """
        self.model.update_turn()

        current_player = self.model.current_player()
        if current_player.crashed:
            logger.debug(f"Player {current_player}'s kart has crashed, skipping their turn")
            return {"success": False}

        speed = current_player.speed
        direction_index = current_player.direction_index

        logger.debug(f"Player {current_player} took action {action_taken}")
        if action_taken == Action.ACCELERATE:
            speed = min(2, speed + 1)
        elif action_taken == Action.BRAKE:
            speed = max(-1, speed - 1)
        elif action_taken == Action.TURN_LEFT:
            direction_index = (direction_index - 1) % 4
        elif action_taken == Action.TURN_RIGHT:
            direction_index = (direction_index + 1) % 4
        elif action_taken == Action.NOTHING:
            logger.debug("Continuing with the same speed and direction.")
        elif action_taken == Action.CHEAT:
            speed += 5
        else:
            logger.critical(f"An invalid action was passed: {action_taken}")
            raise Exception(f"Invalid action passed: {action_taken}")

        current_player.speed = speed
        current_player.direction_index = direction_index
        direction = DIRECTION_ORDER[direction_index]
        return self.process_move_to_position(direction)

    def next_player(self, apply: bool = True) -> Player:
        """
        Advance or preview the next player in turn order.

        Note:
            Players with crashed karts are skipped.

        Args:
            apply (bool): If True, updates the model to the next player and returns that player.
                If False, returns the next player without applying.

        Returns:
            Player: Next player without a crashed kart.
        """
        if len(self.model.players) == 0:
            logger.critical("No players available when trying to switch turns")
            raise ZeroDivisionError("There are no players available in self.model.players")
        
        original_index = self.model.current_player_index

        index = self.model.current_player_index
        for i in range(1, len(self.model.players)):
            index = (index + i) % len(self.model.players)
            
            if not self.model.players[index].crashed:
                self.model.current_player_index = index
                break

        if not apply:
            self.model.current_player_index = original_index
        else:
            logger.debug(f"Next player: {self.model.current_player().name}")

        return self.model.players[index]

    def is_game_over(self) -> bool:
        """
        Check whether the game has ended.

        The game is considered over when at least one player has completed
        the maximum laps or everyone's kart crashed.

        Returns:
            bool: True if the game is finished, False otherwise.
        """
        max_laps_completed = max(laps for laps in self.model.laps_completed.values())
        all_players_crashed = all(player.crashed for player in self.model.players)

        game_over = max_laps_completed == self.model.laps_required or all_players_crashed
        if game_over:
            logger.info("Game over detected")

        return game_over

    def get_leaderboard(self) -> dict:
        """
        Compute final rankings.

        Determines the winner based on laps completed and orders remaining players.

        Returns:
            dict: Contains  
                - 'winner': Player with the most laps completed.  
                - 'losers': Players with fewer laps completed, in descending order.
        """
        temp_level = logger.level
        logger.setLevel(logging.WARNING) # bypass the is_game_over debugging/info logs
        if not self.is_game_over():
            logger.warning("Requested competitive data before game ended")
        logger.setLevel(temp_level)

        # Sort players by laps completed in descending order
        ranking = sorted(
            self.model.laps_completed.items(),
            key=lambda item: (item[1], item[0].nb_turns),
            reverse=True
        )

        winner = ranking[0][0]
        losers = [player_and_laps[0] for player_and_laps in ranking[1:]]

        laps_completed = self.model.laps_completed
        if laps_completed[winner] == laps_completed[losers[0]] and winner.nb_turns == losers[0].nb_turns:
            logger.info(f"It's a draw, there's no winner")
            winner = None

        return {
            "winner": winner,
            "losers": losers
        }
        
    def reset_game_state(self) -> None:
        """
        Reset the underlying game model to its initial state.

        Clears the board and reinitializes players, turn order, etc.
        """
        logger.info("Resetting game state")
        self.model.reset()
