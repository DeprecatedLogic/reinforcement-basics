from player import Human
from engine import GameEngine
from gui import GUI

class GameController:
    """ 
    Orchestrates the interaction between players (Human/AI), engine, and GUI.
    Runs the game loop, forwards actions to the engine, and updates the view when the state changes.
    (Does not contain game rules.)
    """

    def __init__(self, engine: GameEngine, gui: GUI):
        self.game_engine = engine
        self.gui = gui if any(
            [isinstance(player, Human) for player in engine.model.players]
        ) else None
        
    def play(self) -> None:
        """
        Run one complete game until a winner is determined.
        
        Args:
            engine: The game logic, handles game rules and turn handling.
            model: The game model, handles the board state, ownership, score, etc.

        Note:
            Updates player statistics automatically at the end.
        """
        while not self.game_model.is_game_over():
            self.display(self.game_model.current_player.name)
            self.game_engine.make_move(self.game_model.current_player)
            self.update_gui(end_game = False)
        
        winner = self.game_model.get_winner()
        loser = self.game_model.get_loser()
        if winner and loser:
            winner.win()
            loser.lose()
        
        self.update_gui(end_game = True)

    def display_turn(self, name: str):
        print(f"It is {name}'{'s' if not name.endswith('s') else ''} turn.")

    def restart_game(self):
        pass

    def update_gui(self, end_game: bool):
        if not end_game:
            pass
        elif self.gui:
            self.gui.end_game(button_command = self.restart_game)
        else:
            pass