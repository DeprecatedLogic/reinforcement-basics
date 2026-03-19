from cubee.player import Human, Player
from cubee.engine import GameEngine
from cubee.gui import GUI
from cubee.colors import Color
from cubee.cells import Cell

# TODO: import blessed and complete the CLI print functions

class GameController:
    """ 
    Orchestrates the interaction between players (Human/AI), engine, and GUI.
    Runs the game loop, forwards actions to the engine, and updates the view when the state changes.
    (Does not contain game rules.)
    """

    def __init__(self, engine: GameEngine, gui: GUI | None = None):
        """_summary_

        Args:
            engine (GameEngine): _description_
            gui (GUI | None, optional): _description_. Defaults to None.
        """
        self.engine = engine
        self.gui = gui
        self.is_gui_mode = gui is not None
        
    def run(self) -> None:
        """
        Main game loop, blocks until game over.
        """
        initial_state = self.engine.get_initial_state()
        if self.is_gui_mode:
            self._run_gui_mode(initial_state)
        else:
            self._run_cli_mode(initial_state)

    def _run_gui_mode(self, initial_state: dict) -> None:
        """_summary_
        
        Args:
            initial_state (dict): _description_
        """
        self.gui.create_board(
            initial_state["board_rows"],
            initial_state["board_columns"],
            on_cell_click = self._on_cell_clicked
        )
        for player in initial_state["players"]:
            row, column = player.position
            self.gui.update_cell(row, column, player.name, player.color)
        self._update_turn_message(initial_state["current_player"])
    
    def _on_cell_clicked(self, row: int, column: int) -> None:
        """_summary_

        Args:
            row (int): _description_
            column (int): _description_
        """
        response = self.engine.process_move_to_position(row, column)
        if not response["success"]:
            return
        
        current_player = response["player"]
        old_row, old_column = response["old_position"]
        self.gui.update_cell(old_row, old_column, "", None)
        self.gui.update_cell(row, column, current_player.name, current_player.color)
        self.gui.update_board(response["enclosure_modified_cells"], current_player.color)
       
        self._update_turn_message(response["next_player"])

        if self.engine.is_game_over():
            self.gui.end_game(button_command = self.restart_game)
            self._show_game_over_message()

    def _update_turn_message(self, current_player: Player) -> None:
        """_summary_
        
        Args:
            current_player (Player): _description_
        """
        name = current_player.name
        message = f"It is {name}'{'s' if not name.lower().endswith('s') else ''} turn."
        self.gui.update_turn_message(message)

    def _show_game_over_message(self) -> None:
        """_summary_"""
        game_over_data = self.engine.get_competitive_data()
        winner = game_over_data["winner"]
        message = f"Game over! {winner.name} wins!" if winner else "Draw?"
        self.gui.update_turn_message(message)

    def _run_cli_mode(self, initial_state: dict) -> None:
        """_summary_
        
        Args:
            initial_state (dict): _description_
        """
        current_player = initial_state["current_player"]
        while not self.engine.is_game_over():
            self._print_board()
            self._print_turn(current_player)
            
            while True:
                action_taken = current_player.play()
                response = self.engine.process_move(action_taken)
                if response["success"]:
                    break

            self._update_board(response["next_player"], response["enclosure_modified_cells"])
            current_player = response["next_player"]

        result = self.engine.get_competitive_data()
        winner = result["winner"]
        losers = result["losers"]
        cells_counter = result["cells_counter"]

        winner.win()
        for player in losers:
            player.lose()
        
        self._print_game_over(winner, losers, cells_counter)

    def _print_turn(self, current_player: Player) -> None:
        """_summary_
        
        Args:
            current_player (Player): _description_
        """
        name = current_player.name
        message = f"It is {name}'{'s' if not name.lower().endswith('s') else ''} turn."
        print(message)

    def restart_game(self):
        """_summary_"""
        self.engine.reset_game_state()
        self.run()

    def _print_game_over(self, winner: Player, losers: list[Player], cells_counter: dict[Cell, int]) -> None:
        """Prints a centered leaderboard at the end of the game.
        
        Args:
            winner (Player): _description_
            losers (list[Player, ...]): _description_
            cells_counter (dict[Cell, int]): _description_
        """
        players = [winner].extend(losers)
        
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

    def _print_board(self):
        """_summary_"""
        # TODO: Print the board on the terminal with blessed or a similar module
        pass

    def _update_board(self, current_player: Player, cells_modified: list[tuple[int, int]] | None) -> None:
        """_summary_

        Args:
            current_player (Player): _description_
            cells_modified (list[tuple[int, int]): _description_
        """
        if cells_modified:
            # TODO: Update all the cells that were modified
            pass
        else:
            # TODO: Update only the current player's cell
            pass
        