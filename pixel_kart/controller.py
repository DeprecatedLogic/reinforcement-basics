from pixel_kart.player import Human, Player, AI
from pixel_kart.engine import GameEngine
from pixel_kart.actions import Action, KEY_TO_ACTION, AVAILABLE_ACTIONS
from pixel_kart.gui import GUI
import logging
logger = logging.getLogger(__name__)
# TODO: import blessed or similar modules and improve the CLI functions as needed

class GameController:
    """ 
    Orchestrates the interaction between players (Human/AI), engine, and GUI.
    Runs the game loop, forwards actions to the engine, and updates the GUI when the state changes.
    """

    def __init__(self, engine: GameEngine, gui: GUI = None): # Type hint gui as GUI | None when imported
        """
        Initialize the game controller with engine and optional GUI.

        Args:
            engine (GameEngine): The game engine managing rules and state.
            gui (GUI | None, optional): GUI interface for visual interaction. Defaults to None.
        """
        self.engine = engine
        self.gui = gui
        self.gui_locked = False
        
    def run(self, efficiency_level: int = 0) -> None:
        """
        Main game loop, blocks until game is over.

        Args:
            efficiency_level (int): Only for CLI, usually used for increased performance in AI training.  
                0: Default  
                1: No game board output  
                2: No player turn message  
                3: No leaderboard output when the game's over
        """
        logger.info(f"Starting game in {'GUI' if self.gui else 'CLI'} mode")
        game_state = self.engine.get_game_state()
        
        if self.gui:
            self._run_gui_mode(game_state)
        else:
            self._run_cli_mode(game_state, efficiency_level)

    def _run_gui_mode(self, game_state: dict) -> None:
        """
        Set up and run the game in GUI mode, initializing board and player positions.
        
        Args:
            game_state (dict): Initial game state from the engine.
        """
        logger.debug("Initializing GUI board")
        
        # Tell GUI to draw the track based on the grid
        board_grid = game_state["board"].grid
        self.gui.create_board(board_grid)

        logger.debug("Binding key events to GUI")
        self.gui.bind_keys(self._on_keypress)

        # Initial render of all players
        all_players = [game_state["current_player"]] + list(game_state["opponents"])
        self.gui.update_karts(all_players)
        self.gui.update_hud(game_state["current_player"], game_state["laps_completed"])

        self._update_turn_message(game_state["current_player"])

        # If the first player is a bot (automate player), kick off their turn automatically
        if not isinstance(game_state["current_player"], Human):
            logger.debug("GUI locked, keypress events will be discarded")
            self.gui_locked = True
            self._handle_automated_turn(gui_event=True)

    def _on_keypress(self, event) -> None:
        """
        Handle a key press in the GUI, mapping it to a player action.

        Args:
            event: Tkinter keypress event.
        """
        if self.gui_locked:
            logger.debug("GUI is locked, keypress event discarded")
            return

        # Lowercase the Tkinter input to match our foolproof KEY_TO_ACTION dictionary
        key = event.keysym.lower()
        logger.debug(f"Key pressed: {key}")

        action_taken = KEY_TO_ACTION.get(key)
        
        # We check 'is not None' just in case Action.NOTHING evaluates to False in some contexts
        if action_taken is not None:
            response = self.engine.process_move(action_taken)

            self._handle_move_response()
            
            # Check if next player is an automated player
            game_state = self.engine.get_game_state()
            if not isinstance(game_state["current_player"], Human) and not game_state["is_game_over"]:
                logger.debug("GUI locked, keypress events will be discarded")
                self.gui_locked = True
                self._handle_automated_turn(gui_event=True)

    def _handle_automated_turn(self, gui_event: bool = False) -> dict:
        """
        Execute a single AI turn and optionally propagate updates to the GUI.
        """
        game_state = self.engine.get_game_state()
        automated_player: AI | Player = game_state["current_player"]

        if isinstance(automated_player, AI):
            action_taken = automated_player.play(game_state)
        else:
            action_taken = automated_player.play(AVAILABLE_ACTIONS)
        response = self.engine.process_move(action_taken)
        
        # TODO: [IMPORTANT] Depending on how the AI class is set up, we might need to adjust compute_reward args
        if hasattr(automated_player, "compute_reward"):
            automated_player.compute_reward(game_state, response)

        if gui_event:
            self._handle_move_response()
            
            new_state = self.engine.get_game_state()
            if not new_state["is_game_over"] and not isinstance(new_state["current_player"], Human):
                    # Schedule next automated turn with a small delay so human can see it happen
                    self.gui.parent.after(200, lambda: self._handle_automated_turn(gui_event=True))
            else:
                logger.debug("GUI unlocked, listening to keypress events")
                self.gui_locked = False

        return response # required for CLI

    def _handle_move_response(self) -> None:
        """
        Update the GUI after a move has been successfully processed.
        """
        game_state = self.engine.get_game_state()
        all_players = list(game_state["opponents"]) + [game_state["current_player"]]
        
        # Tell GUI to redraw the karts in their new positions/rotations
        self.gui.update_karts(all_players)
        
        # Update speed/lap counters on screen
        self.gui.update_hud(game_state["current_player"], game_state["laps_completed"])
        self._update_turn_message(game_state["current_player"])

        if game_state["is_game_over"]:
            logger.info("Game over (GUI)")
            leaderboard = self.engine.get_leaderboard()
            self.gui.end_game(button_command=self.restart_game)
            self._show_game_over_message(leaderboard)

    def _update_turn_message(self, current_player: Player) -> None:
        """Update the turn message in the GUI."""
        name = current_player.name
        message = f"It is {name}'{'s' if not name.lower().endswith('s') else ''} turn."
        self.gui.update_turn_message(message)

    def _show_game_over_message(self, leaderboard: dict|None = None) -> None:
        """Display the final game over message in the GUI."""
        if not leaderboard:
            leaderboard = self.engine.get_leaderboard() 
        winner = leaderboard["winner"]
        if winner is None:
            logger.info(f"")
            
        logger.info(f"Winner: {winner.name if winner else 'None'}")
        message = "Game over! "
        message += f"{winner.name} wins!" if winner else "It's a draw!"
        self.gui.update_turn_message(message)

    def _run_cli_mode(self, game_state: dict, efficiency_level: int = 0) -> None:
        """
        Run the game loop in CLI mode, printing board and turn messages.

        Args:
            game_state (dict): Initial game state from the engine.
        """
        logger.info(f"Running CLI game loop with efficiency level {efficiency_level}")

        while not self.engine.is_game_over():
            current_player = game_state["current_player"]
            
            logger.debug(f"Turn: {current_player.name}")
            if efficiency_level < 2:
                if efficiency_level == 0: self._update_board(game_state)
                self._print_turn(current_player)
            
            if not isinstance(current_player, Human):
                response = self._handle_automated_turn()
            else:
                while True:
                    # For CLI human testing, play() would need to prompt for input
                    action_taken = current_player.play([]) 
                    response = self.engine.process_move(action_taken)
                    if response.get("success"):
                        break
            
            if efficiency_level < 1:
                game_state = self.engine.get_game_state() # update the game state
                self._update_board(game_state)
            else: # update only current player (the rest of the data doesn't matter)
                game_state["current_player"] = response["current_player"]

        logger.info("Game over (CLI)")
        # Calculate stats for CLI game over
        if efficiency_level < 3: 
            self._print_game_over(game_state)

    def _print_turn(self, current_player: Player) -> None:
        name = current_player.name
        message = f"It is {name}'{'s' if not name.lower().endswith('s') else ''} turn."
        print(message)

    def restart_game(self, efficiency_level: int = 0) -> None:
        logger.info("Restarting game")
        # Reset the game
        self.engine.reset_game_state() 
        self.run(efficiency_level)

    def _print_game_over(self, game_state: dict) -> None:
        """
        Print the final leaderboard and scores at the end of the game.
        
        Args:
            game_state (dict): Initial game state from the engine.
        """
        logger.debug("Printing leaderboard")

        laps_completed = game_state["laps_completed"]
        
        leaderboard = self.engine.get_leaderboard()
        winner = leaderboard["winner"]
        losers = leaderboard["losers"]
        leaderboard = [winner] + losers

        print("=" * 40)
        print("LEADERBOARD".center(40))
        print("=" * 40)

        for placement, player in enumerate(leaderboard, start=1):
            laps = laps_completed[player]
            prefix = "🏆" if placement == 1 else f"{placement}."
            print(f"{prefix} {player.name} | Laps: {laps}".center(40))

        print("=" * 40)

    def _print_board(self, game_state: dict) -> None:
        """
        Print a simple CLI representation of the board.

        Args:
            game_state (dict): Initial game state from the engine.
        """
        # Uses the board's __str__ method
        print(game_state["board"])

    def _update_board(self, game_state: dict) -> None:
        """
        Update the CLI board after a move. Currently prints the full board.

        Args:
            game_state (dict): Initial game state from the engine.
        """
        # TODO: Improve by updating only modified cells + adding colors (or player initials/emoticons?)
        self._print_board(game_state)
