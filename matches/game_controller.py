from matches.game_model import GameModel
from matches.player import Player, Human, AI
from matches.game_view import GameView

class GameController:
    """Mediator between the game model (logic) and view (GUI)."""
    def __init__(self, player1, player2, nb_matches):
        """
        Set up a new game session with GUI.

        Args:
            player1: First player (can be Human or AI)
            player2: Second player (can be Human or AI)
            nb_matches: Initial number of matches
        """

        self.action_taken = 0
    
        # Initialisation of model
        self.model = GameModel(nb_matches, player1, player2)
        
        # Skip GUI when 2 AIs are playing
        if all(isinstance(player, AI) for player in self.model.players):
            self.model.play()
            return
        
        # Initialisation of view
        self.view = GameView(self)
        
        #If AI is first to play, we make him play straight away
        if not isinstance(self.model.get_current_player(), Human):
            self.handle_ai_move()

        self.start()

    def start(self) -> None:
        """Launch the Tkinter main event loop."""
        self.view.mainloop()

    def get_nb_matches(self) -> int:
        """Return current number of matches remaining."""
        return self.model.nb
    
    def get_status_message(self) -> str:
        """Generate appropriate status text for display."""
        if self.model.is_game_over():
            winner = self.model.get_winner()
            return f"Game has concluded! {winner.name} won!"
        
        current = self.model.get_current_player()
        return f"It is {current.name}'s turn."
    
    def reset_game(self):
        """Reset model to initial state, refresh GUI and make AI play if it's his turn after reset."""
        self.action_taken = 0
        self.model.reset()
        
         # Skip GUI when 2 AIs are playing
        if all(isinstance(player, AI) for player in self.model.players):
            self.model.play()
            return
        
        self.view.reset()
        self.view.update_view()

        #AI plays straight away if he is first after reset
        if not isinstance(self.model.get_current_player(), Human):
            self.handle_ai_move()

    def handle_human_move(self, action) -> None:
        """
        Process a move made by the human player, make AI play if it's his turn after the move
        and update the view.

        Args:
            action: Number of matches the human chose to remove
        """
        current_player = self.model.get_current_player()

        if isinstance(current_player, Human):
            self.action_taken = action
            self.model.step(action)

            if self.model.is_game_over():
                self.handle_end_game()
            else:
                self.model.switch_player()
                if not isinstance(self.model.get_current_player(), Human):
                    self.view.update_view()
                    self.handle_ai_move()

            self.view.update_view()

    def handle_ai_move(self) -> None:
        """Execute one move by the AI player and update the view."""
        current_player = self.model.get_current_player()

        action = current_player.play()
        action = min(action, self.model.nb)
        self.action_taken = action

        self.model.step(action)

        if self.model.is_game_over():
            self.handle_end_game()
        else:
            self.model.switch_player()

        self.view.update_view()

    def handle_end_game(self) -> None:
        """Update player statistics and switch GUI to game-over state."""
        winner = self.model.get_winner()
        loser = self.model.get_loser()

        winner.win()
        loser.lose()

        self.view.end_game()