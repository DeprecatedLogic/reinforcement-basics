from model import GameModel

class GameEngine:
    """
    Implements the rules and flow of the game.
    Validates moves, updates the board through the model, triggers enclosure detection when required,
        switches turns, and determines game outcome.
    (Contains no UI logic.)
    """
    
    def __init__(self, model: GameModel):
        self.model = model

    def make_move(self):
        
        actions_available = []
        
        # player plays then we switch
        action = self.model.current_player.play(actions_available)
        self.switch_player()

    def check_enclosure(self):
        """ BFS implementation """
        pass
    
    def switch_player(self) -> None:
        """Get the next player."""
        if self.model.current_player == self.players[0]:
            self.model.current_player = self.players[1]
        else:
            self.model.current_player = self.players[0]