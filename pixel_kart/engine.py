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
        self.allowed_speed_range = (-1, 2)

    def get_game_state(self) -> dict:
        """
        Build and return a snapshot of the current game state.

        Returns:
            dict: Snapshot mapping representing the current state containing keys:
                  - "board": The active Board grid model instance.
                  - "current_player": Player instance taking the current turn.
                  - "opponents": Tuple of other players on the track.
                  - "is_game_over": Boolean indicating if ending conditions are met.
                  - "laps_completed": Reference dict mapping players to completed laps.
                  - "laps_required": Integer target required to win.
        """
        board = self.model.board
        player = self.model.current_player()
        opponents = self.model.get_opponents()
        #next_player = self.next_player(apply=False)
        is_game_over = self.is_game_over()

        return {
            "board": board,
            "current_player": player,
            "opponents": opponents,
            #"next_player": next_player,
            #"relative_vision_cells": relative_vision_cells,
            "is_game_over": is_game_over,
            "laps_completed": self.model.laps_completed,
            "laps_required": self.model.laps_required
        }

    def _should_crash(self, row: int, column: int) -> bool:
        """
        Evaluate if moving to the specified coordinates results in a kart crash.

        Args:
            row (int): Target row index grid line.
            column (int): Target column index grid line.

        Returns:
            bool: True if position is out of bounds or strikes a wall; otherwise False.
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
        """
        Apply physics environmental slowdown/speedup factors to the player's current velocity.

        Note:
            Moving across a `Cell.GRASS` tile cuts velocity in half via integer truncation, 
            driving both forward vectors and reverse vectors smoothly towards zero.

        Args:
            board_cell (Cell): The bitfield flag tracking terrain properties of the active cell.
            speed (int): The current speed value of the moving player.

        Returns:
            int: The adjusted speed value following environmental surface attenuation.
        """
        if board_cell & Cell.GRASS:
            # Use `speed // 2` if going backward should be a constant -1
            speed = int(speed / 2) # drives both 1 and -1 towards 0 (slows down both directions)

        return speed

    def process_move_to_position(self, direction: Direction) -> dict:
        """
        Process the step-by-step physical displacement of a player along a directional vector.

        Note:
            If velocity is negative, the orientation vector is inverted 180 degrees 
            to simulate reverse locomotion. Physics calculations, surface friction adjustments, 
            boundary checks, and anti-cheat telemetry are evaluated individually for each step. 
            If a crash occurs, execution ceases early for that player.

        Args:
            direction (Direction): The absolute orientation heading guiding kart displacement.

        Returns:
            dict: Event properties reporting state metrics back to the orchestration loop:
                  - "success": Boolean execution confirmation (always True).
                  - "old_player": Player instance evaluated during this turn.
                  - "current_player": The next player up in rotation order.
                  - "is_cheating": Boolean flag flagging illegal layout leaps.
                  - "has_completed_lap": True if a valid lap was completed this turn.
                  - "checkpoint_acquired": True if a checkpoint was unlocked this turn.
                  - "is_game_over": True if a terminal ending match pattern was activated.
        """
        board = self.model.board
        current_player = self.model.current_player()
        position = current_player.position
        speed = current_player.speed
        has_checkpoint = current_player.checkpoint
        checkpoint_acquired = False
        laps_completed = self.model.laps_completed[current_player]
        steps = abs(speed)
        cell = board[position]
        is_stationary = steps == 0
        has_completed_lap = False # False by default
        #cells_in_path = [board[position]]
        is_cheating = False # False by default

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
                    direction_delta = DIRECTION_ORDER[direction_index].delta # Use direction_deltas ?

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
                    #cells_in_path.append(cell)

                    # Apply speed effects and update the player's speed value
                    current_player.speed = speed = self._apply_speed_effects(cell, speed)
                    
                    # Run the anti-cheat (resolves all kinds of cheating + counts laps!)
                    is_cheating = self._anti_cheat(current_player, original_position=position)
                    if is_cheating:
                        logger.info(f"Player {current_player} was found cheating")
                        break
        
                    if laps_completed < self.model.laps_completed[current_player]:
                        has_completed_lap = True

                    if not has_checkpoint and current_player.checkpoint:
                        checkpoint_acquired = True

        self.next_player()

        # Adjust the data returned based on Controller requirements
        return {
            "success": True,
            "old_player": current_player,
            #"cells_in_path": cells_in_path, # for whatever reason...
            "current_player": self.model.current_player(),
            #"is_stationary": is_stationary,
            "is_cheating": is_cheating,
            "has_completed_lap": has_completed_lap,
            "checkpoint_acquired": checkpoint_acquired,
            "is_game_over": self.is_game_over()
        }

    def _anti_cheat(self, player: Player, original_position: tuple[int, int]) -> bool:
        """
        Validate speed metrics and enforce correct track sequence checkpoints.

        Note:
            If speed bounds are violated, velocity resets to 0 and the player resets 
            to their turn-start position. 
            
            Laps are incremented only when passing the finish line while possessing 
            both `start_line` and `checkpoint` validations. Passing a finish line resets 
            both tracking flags to False.

        Args:
            player (Player): The player instance currently undergoing evaluation.
            original_position (tuple[int, int]): Coords pointing to the player's turn-start position.

        Returns:
            bool: True if an illegal velocity modification or sequence shortcut was caught.
        """
        board = self.model.board
        cell = board[player.position]
        is_cheating = False

        # Check if player is moving faster than allowed
        min_speed_allowed = min(self.allowed_speed_range)
        max_speed_allowed = max(self.allowed_speed_range)

        if player.speed < min_speed_allowed or player.speed > max_speed_allowed:
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
        Apply structural steering or engine adjustments before resolving movement physics.

        Args:
            action_taken (Action): The game action item to apply to the active player.

        Returns:
            dict: Result mapping containing data forwarded from `process_move_to_position`.
                  Returns `{"success": False}` early if the current player is already crashed.

        Raises:
            Exception: If an unmapped or invalid Action enum entry reaches this handler.
        """
        self.model.update_turn()

        current_player = self.model.current_player()
        if current_player.crashed:
            logger.debug(f"Player {current_player}'s kart has crashed, skipping their turn")
            return {"success": False}

        speed = current_player.speed
        direction_index = current_player.direction_index

        min_speed_allowed = min(self.allowed_speed_range)
        max_speed_allowed = max(self.allowed_speed_range)
        number_of_directions = len(DIRECTION_ORDER)

        logger.debug(f"Player {current_player} took action {action_taken}")
        if action_taken == Action.ACCELERATE:
            speed = min(max_speed_allowed, speed + 1)
        elif action_taken == Action.BRAKE:
            speed = max(min_speed_allowed, speed - 1)
        elif action_taken == Action.TURN_LEFT:
            direction_index = (direction_index - 1) % number_of_directions
        elif action_taken == Action.TURN_RIGHT:
            direction_index = (direction_index + 1) % number_of_directions
        elif action_taken == Action.NOTHING:
            logger.debug("Continuing with the same speed and direction.")
        elif action_taken == Action.CHEAT: # TESTING PURPOSES
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

        Note:
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

        Note:
            If the leader crashes without completing the lap count requirements, 
            they are disqualified, resulting in an open DNF bracket with no winner.

        Returns:
            dict: Contains  
                - 'winner': Player instance matching victory criteria, or None.
                - 'losers': Ordered list of remaining participants.
        """
        temp_level = logger.level
        logger.setLevel(logging.WARNING) # bypass the is_game_over debugging/info logs
        if not self.is_game_over():
            logger.warning("Requested competitive data before game ended")
        logger.setLevel(temp_level)

        # Sort players by laps completed in descending order
        ranking = sorted(
            self.model.laps_completed.items(),
            key=lambda item: item[1],
            reverse=True
        )

        winner = ranking[0][0]
        losers = [player_and_laps[0] for player_and_laps in ranking[1:]]

        laps_completed = self.model.laps_completed

        # If the "winner" crashed without finishing the required laps, they are disqualified
        if winner and winner.crashed and laps_completed[winner] < self.model.laps_required:
            logger.info("The last surviving player crashed. No winner.")
            winner = None
            losers = list(self.model.players) # Everyone goes to the losers bracket

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
