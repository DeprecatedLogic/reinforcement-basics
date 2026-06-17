from pixel_kart.player import Human, Player, AI
from pixel_kart.engine import GameEngine
from pixel_kart.actions import Action, KEY_TO_ACTION, AVAILABLE_ACTIONS
from pixel_kart.gui import GUI
import logging
logger = logging.getLogger(__name__)
# TODO: import blessed or similar modules and improve the CLI functions as needed

class GameController:
    """
    Orchestrates execution loops between game agents, rule engines, and visual interfaces.

    Acts as the top-level finite state coordinator. Manages absolute step phases, 
    routes user interface keystrokes or machine learning exploratory decisions to the 
    underlying physics simulators, and flushes terminal reinforcement training metrics.
    """

    def __init__(self, engine: GameEngine, gui: GUI | None = None) -> None:
        """
        Initialize the coordinator with an execution rules engine and optional interface layer.

        Args:
            engine (GameEngine): The rule and state tracking engine instance.
            gui (GUI, optional): The Tkinter window or display panel overlay. Defaults to None.
        """
        self.engine = engine
        self.gui = gui
        self.gui_locked = False
        
    def run(self, efficiency_level: int = 0) -> None:
        """
        Execute the master blocking operational loop until match ending invariants are achieved.

        Note:
            In GUI mode, ownership of the main execution thread shifts to Tkinter's event 
            dispatch loops. In CLI mode, the system tracks steps iteratively in a while loop. 
            Once the rule engine reports a terminal flag, final winner-bracket allocations are 
            computed and pushed to learning agents.

        Args:
            efficiency_level (int, optional): Performance profile limiting terminal output:
                - 0: Default full verbosity logging.
                - 1: Strips layout grid printing loops.
                - 2: Strips step rotation details messages.
                - 3: Strips leaderboard tables display metrics at conclusion intervals.
        """
        logger.info(f"Starting game in {'GUI' if self.gui else 'CLI'} mode")
        game_state = self.engine.get_game_state()
        
        if self.gui:
            self._run_gui_mode(game_state)
        else:
            self._run_cli_mode(game_state, efficiency_level)

    def _run_gui_mode(self, game_state: dict) -> None:
        """
        Set up and run the game in GUI mode, initializing board layouts and player positions.
        
        Args:
            game_state (dict): Initial game state snapshot from the engine.
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
            self._handle_automated_turn(game_state, gui_event=True)

    def _on_keypress(self, event) -> None:
        """
        Handle a key press in the GUI, mapping it to a player action.

        Args:
            event: Tkinter keypress event payload.
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

            game_state = self.engine.get_game_state()
            self._handle_move_response(game_state)
            
            # Check if next player is an automated player
            if not isinstance(game_state["current_player"], Human) and not game_state["is_game_over"]:
                logger.debug("GUI locked, keypress events will be discarded")
                self.gui_locked = True
                self._handle_automated_turn(game_state, gui_event=True)

    def _handle_automated_turn(self, game_state: dict, gui_event: bool = False) -> dict:
        """
        Execute a single AI or bot turn and optionally propagate updates to the GUI.

        Args:
            game_state (dict): The current game state tracker dictionary.
            gui_event (bool): Flag indicating if GUI loops should schedule sequential turns.

        Returns:
            dict: The response payload dict from the engine processing move.
        """
        automated_player: AI | Player = game_state["current_player"]

        if isinstance(automated_player, AI):
            action_taken = automated_player.play(game_state)
        else:
            action_taken = automated_player.play(AVAILABLE_ACTIONS)
        response = self.engine.process_move(action_taken)
        
        new_state = None
        if isinstance(automated_player, AI):
            new_state = self.engine.get_game_state()
            automated_player.compute_reward(new_state, response)

        if gui_event:
            if new_state is None:
                new_state = self.engine.get_game_state()

            self._handle_move_response(new_state)

            if not new_state["is_game_over"] and not isinstance(new_state["current_player"], Human):
                    # Schedule next automated turn with a small delay so humans can see it happen
                    self.gui.parent.after(200, lambda: self._handle_automated_turn(game_state=new_state, gui_event=True))
            else:
                logger.debug("GUI unlocked, listening for keypress events")
                self.gui_locked = False

        return response # required for CLI

    def _handle_move_response(self, game_state: dict) -> None:
        """
        Update the GUI after a move has been successfully processed based on the game's state.

        Args:
            game_state (dict): The current game state tracker snapshot.
        """
        all_players = list(game_state["opponents"]) + [game_state["current_player"]]
        
        # Tell GUI to redraw the karts in their new positions/rotations
        self.gui.update_karts(all_players)
        
        # Update speed/lap counters on screen
        self.gui.update_hud(game_state["current_player"], game_state["laps_completed"])
        self._update_turn_message(game_state["current_player"])

        if game_state["is_game_over"]:
            logger.info("Game over (GUI)")

            # Get leaderboard and apply AI rewards that have yet to be applied (if any)
            leaderboard = self._handle_game_over_sweep(game_state)

            self.gui.end_game(button_command=self.restart_game)
            self._show_game_over_message(leaderboard)

    def _handle_game_over_sweep(self, game_state: dict) -> dict:
        """
        Distribute win/lose signals and force terminal Q-Table updates for non-crashed AI.

        Args:
            game_state (dict): The final game state snapshot.

        Returns:
            dict: The sorted leaderboard dictionary from the engine.
        """
        leaderboard = self.engine.get_leaderboard()
        winner = leaderboard["winner"]
        losers = leaderboard["losers"]

        # Distribute Win/Lose signals
        if winner:
            winner.win()
        for loser in losers:
            loser.lose()

        # This is unnecessary because terminal Q-table update
        # has been moved into Win/Lose methods.
        """
        # Force terminal Q-Table updates for all AI
        all_players = list(game_state["opponents"]) + [game_state["current_player"]]
        for player in all_players:
            if isinstance(player, AI) and not player.crashed:
                player.force_terminal_update()
        """

        return leaderboard

    def _update_turn_message(self, current_player: Player) -> None:
        """
        Update the informational turn tracking message inside the GUI text elements.

        Args:
            current_player (Player): Active entity whose turn is currently processed.
        """
        name = current_player.name
        message = f"It is {name}'{'s' if not name.lower().endswith('s') else ''} turn."
        self.gui.update_turn_message(message)

    def _show_game_over_message(self, leaderboard: dict|None = None) -> None:
        """
        Display the final game over victory text message in the GUI window frame.

        Args:
            leaderboard (dict, optional): Complete results mapping standings. Defaults to None.
        """
        if not leaderboard:
            leaderboard = self.engine.get_leaderboard() 
        winner = leaderboard["winner"]
            
        logger.info(f"Winner: {winner.name if winner else 'None'}")
        message = "Game over! "
        message += f"{winner.name} wins!" if winner else "It's a draw!"
        self.gui.update_turn_message(message)

    def _run_cli_mode(self, game_state: dict, efficiency_level: int = 0) -> None:
        """
        Run the interactive main step sequence loop inside command line environments.

        Args:
            game_state (dict): Initial game state configuration parameters.
            efficiency_level (int, optional): Log throttling intensity value bounds. Defaults to 0.
        """
        logger.info(f"Running CLI game loop with efficiency level {efficiency_level}")

        while not self.engine.is_game_over():
            current_player = game_state["current_player"]
            
            logger.debug(f"Turn: {current_player.name}")
            if efficiency_level < 2:
                if efficiency_level == 0: self._update_board(game_state)
                self._print_turn(current_player)
            
            if not isinstance(current_player, Human):
                response = self._handle_automated_turn(game_state)
            else: # This will throw an error (TODO: handle it maybe ?)
                while True:
                    # For CLI human testing, play() would need to prompt for input
                    action_taken = current_player.play([]) 
                    response = self.engine.process_move(action_taken)
                    if response.get("success"):
                        break
            
            game_state = self.engine.get_game_state() # update the game state
            if efficiency_level < 1:
                self._update_board(game_state)

        leaderboard = self._handle_game_over_sweep(game_state)

        logger.info("Game over (CLI)")
        # Calculate stats for CLI game over
        if efficiency_level < 3: 
            self._print_game_over(game_state, leaderboard)

    def _print_turn(self, current_player: Player) -> None:
        """
        Format and stream current turn notifications to the stdout buffer.

        Args:
            current_player (Player): Active profile whose actions are being evaluated.
        """
        name = current_player.name
        message = f"It is {name}'{'s' if not name.lower().endswith('s') else ''} turn."
        print(message)

    def restart_game(self, efficiency_level: int = 0) -> None:
        """
        Wipe out active variables, trigger engine resets, and restart loops.

        Args:
            efficiency_level (int, optional): Performance profiling floor bounds filter. Defaults to 0.
        """
        logger.info("Restarting game")
        # Reset the game
        self.engine.reset_game_state() 
        self.run(efficiency_level)

    def _print_game_over(self, game_state: dict, leaderboard: dict) -> None:
        """"
        Print the final leaderboard table and total lap scores to stdout at match conclusion.
        
        Args:
            game_state (dict): Initial game state snapshot from the engine.
            leaderboard (dict): Mapping detailing the finalized competitive standing arrays.
        """
        logger.debug("Printing leaderboard")

        laps_completed = game_state["laps_completed"]

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
        Print a simple ASCII grid text representation of the circuit board.

        Args:
            game_state (dict): Active context tracking mapping properties.
        """
        # Uses the board's __str__ method
        print(game_state["board"])

    def _update_board(self, game_state: dict) -> None:
        """
        Redraw the command line interface track board layer sequence following moves.

        Args:
            game_state (dict): Active context mapping parameters.
        """
        # TODO: Improve by updating only modified cells + adding colors (or player initials/emoticons?)
        self._print_board(game_state)
