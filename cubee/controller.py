from cubee.player import Human, Player, AI
from cubee.engine import GameEngine
from cubee.gui import GUI
from cubee.colors import Color
from cubee.cells import Cell
from cubee.actions import ACTION_DELTAS, KEY_TO_ACTION
import logging
logger = logging.getLogger(__name__)
# TODO: import blessed or similar modules and improve the CLI functions as needed

class GameController:
    """ 
    Orchestrates the interaction between players (Human/AI), engine, and GUI.
    Runs the game loop, forwards actions to the engine, and updates the view when the state changes.
    """

    def __init__(self, engine: GameEngine, gui: GUI | None = None):
        """
        Initialize the game controller with engine and optional GUI.

        Args:
            engine (GameEngine): The game engine managing rules and state.
            gui (GUI | None, optional): GUI interface for visual interaction. Defaults to None.
        """
        self.engine = engine
        self.gui: GUI = gui
        self.gui_locked = False
        
    def run(self, efficiency_level: int = 0) -> None:
        """
        Main game loop, blocks until game over.

        Args:
            efficieny_level (int): Only for CLI, usually used for increased performance in AI training.  
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
        self.gui.create_board(
            game_state["board_rows"],
            game_state["board_columns"],
            on_cell_click = self._on_cell_clicked
        )

        logger.debug("Binding key events to GUI")
        self.gui.bind_keys(self._on_keypress)

        players = list(game_state["opponents"])
        players.append(game_state["current_player"])
        for player in players:
            logger.debug(f"Placing {player.name} at {player.position}")

            row, column = player.position
            self.gui.update_cell(row, column, player.name, player.color)

        self._update_turn_message(game_state["current_player"])

        if isinstance(game_state["current_player"], AI):
            self.gui_locked = True
            self._handle_ai_turn(gui_event=True)
    
    def _on_cell_clicked(self, row: int, column: int) -> None:
        """
        Handle a cell click in the GUI by processing the move through the engine.

        Args:
            row (int): Row index of the clicked cell.
            column (int): Column index of the clicked cell.
        """
        logger.debug(f"Cell clicked at ({row}, {column})")
        if self.gui_locked:
            logger.debug("GUI is locked, cell click event discarded")
            return

        response = self.engine.process_move_to_position(row, column)
        if not response["success"]:
            logger.debug("Move rejected")
            return

        self._handle_move_response(response)
        if isinstance(response["current_player"], AI) and not response["is_game_over"]:
            self._handle_ai_turn(gui_event=True)

    def _on_keypress(self, event) -> None:
        """
        Handle a key press in the GUI, mapping it to a player action.

        Args:
            event: Tkinter keypress event.
        """
        key = event.keysym.lower()
        logger.debug(f"Key pressed: {key}")
        if self.gui_locked:
            logger.debug("GUI is locked, keypress event discarded")
            return

        action_taken = KEY_TO_ACTION.get(key)
        if action_taken:

            response = self.engine.process_move(action_taken)
            if not response["success"]:
                logger.debug("Move rejected")
                return

            self._handle_move_response(response)
            if isinstance(response["current_player"], AI) and not response["is_game_over"]:
                self._handle_ai_turn(gui_event=True)    

    def _handle_ai_turn(self, gui_event: bool = False) -> dict:
        """_summary_

        Returns:
            dict: _description_
        """
        game_state = self.engine.get_game_state()
        ai_player: AI = game_state["current_player"]

        action_taken = ai_player.play(game_state)
        response = self.engine.process_move(action_taken)
        
        ai_player.compute_reward(game_state, action_taken, response)

        if gui_event:
            self._handle_move_response(response)

            if not response["is_game_over"] and isinstance(response["current_player"], AI):
                self.gui.parent.after(1000, lambda: self._handle_ai_turn(gui_event=True))
            else:
                self.gui_locked = False

        return response # required for CLI
    
    def _handle_move_response(self, response: dict) -> None:
        """
        Update the GUI after a move has been processed.

        Args:
            response (dict): Engine response containing move result and modified cells.
        """
        current_player = response["old_player"]
        row, column = current_player.position
        old_row, old_column = response["old_position"]
        self.gui.update_cell(old_row, old_column, "", None)
        self.gui.update_cell(row, column, current_player.name, current_player.color)
        self.gui.update_board(response["enclosure_modified_cells"], current_player.color)
        logger.debug(f"{current_player.name} moved to ({row}, {column})")

        self._update_turn_message(response["current_player"])

        if self.engine.is_game_over():
            logger.info("Game over (GUI)")
            self.gui.end_game(button_command=self.restart_game)
            self._show_game_over_message()

    def _update_turn_message(self, current_player: Player) -> None:
        """
        Update the turn message in the GUI to show which player's turn it is.

        Args:
            current_player (Player): Player whose turn it currently is.
        """
        name = current_player.name
        message = f"It is {name}'{'s' if not name.lower().endswith('s') else ''} turn."
        self.gui.update_turn_message(message)

    def _show_game_over_message(self) -> None:
        """
        Display the final game over message in the GUI with the winner.
        """
        game_over_data = self.engine.get_competitive_data()
        winner = game_over_data["winner"]
        
        logger.info(f"Winner: {winner.name if winner else 'None'}")
        message = f"Game over! {winner.name} wins!" if winner else "Draw?"
        self.gui.update_turn_message(message)

    def _run_cli_mode(self, game_state: dict, efficiency_level: int = 0) -> None:
        """
        Run the game loop in CLI mode, printing board and turn messages.

        Args:
            game_state (dict): Initial game state from the engine.
            efficieny_level (int): Usually used for increased performance in AI training.  
                0: Default  
                1: No game board output  
                2: No player turn message  
                3: No leaderboard output when the game's over
        """
        logger.info(f"Running CLI game loop with efficiency level {efficiency_level}")

        current_player = game_state["current_player"]
        while not self.engine.is_game_over():
            logger.debug(f"Turn: {current_player.name}")
            if efficiency_level < 2:
                if efficiency_level == 0: self._print_board()
                self._print_turn(current_player)
            
            if isinstance(current_player, AI):
                    response = self._handle_ai_turn()
            else:
                while True:
                    action_taken = current_player.play()

                    response = self.engine.process_move(action_taken)
                    if response["success"]:
                        break
                    else:
                        logger.debug(f"{current_player.name} attempted invalid move: {action_taken}")

            if efficiency_level < 1: self._update_board(response["current_player"], response["enclosure_modified_cells"])
            current_player = response["current_player"]

        result = self.engine.get_competitive_data()
        winner = result["winner"]
        losers = result["losers"]
        cells_counter = result["cells_counter"]

        winner.win()
        for player in losers:
            player.lose()

        logger.info("Game over (CLI)")
        logger.info(f"Winner: {winner.name}")
        if efficiency_level < 3: self._print_game_over(winner, losers, cells_counter)

    def _print_turn(self, current_player: Player) -> None:
        """
        Print a message indicating whose turn it is in CLI mode.

        Args:
            current_player (Player): Player whose turn it currently is.
        """
        logger.debug(f"Displaying turn for {current_player.name}")

        name = current_player.name
        message = f"It is {name}'{'s' if not name.lower().endswith('s') else ''} turn."
        print(message)

    def restart_game(self, efficiency_level: int = 0):
        """
        Reset the game state and start a new game loop.

        Args:
            efficieny_level (int): Only for CLI, usually used for increased performance in AI training.  
                0: Default  
                1: No game board output  
                2: No player turn message  
                3: No leaderboard output when the game's over
        """
        logger.info("Restarting game")
        self.engine.reset_game_state()
        self.run(efficiency_level)

    def _print_game_over(self, winner: Player, losers: list[Player], cells_counter: dict[Cell, int]) -> None:
        """
        Print the final leaderboard and scores at the end of the game.

        Args:
            winner (Player): Player who won the game.
            losers (list[Player, ...]): Players who lost.
            cells_counter (dict[Cell, int]): Number of cells owned by each player.
        """
        logger.debug("Printing leaderboard")
        
        players = [winner] + losers
        
        # calculate the total width based on the longest name + score
        width_name = max(len(player.name) for player in players)
        width_score = max(len(str(cells_counter[player.cell])) for player in players)
        total_width = width_name + width_score + 7  # padding + separator

        print("=" * total_width)
        print(f"{'LEADERBOARD'.center(total_width)}")
        print("=" * total_width)

        # print winner
        winner_score = cells_counter[winner.cell]
        winner_line = f"🏆 {winner.name} | Score: {winner_score}"
        print(winner_line.center(total_width))

        # print losers
        for placement, player in enumerate(losers, start=1):
            score = cells_counter[player.cell]
            line = f"{placement}. {player.name} | Score: {score}"
            print(line.center(total_width))

        print("=" * total_width)

    def _print_board(self) -> None:
        """
        Print a simple CLI representation of the board.
        """
        # TODO: Enhance CLI board with player colors, symbols, or partial updates
        board = self.engine.model.board
        print(board) # uses the board's __str__ method

    def _update_board(self, current_player: Player, cells_modified: list[tuple[int, int]] | None) -> None:
        """
        Update the CLI board after a move. Currently prints the full board.

        Args:
            current_player (Player): Player who just moved.
            cells_modified (list[tuple[int, int]] | None): Cells affected by enclosure.
        """
        # TODO: Improve by updating only modified cells + adding colors (or player initials/emoticons?)
        self._print_board()
        