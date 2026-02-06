from matches.game_model import GameModel
from matches.player import Player, Human
from matches.game_view import GameView

class GameController:
    def __init__(self, player1, player2, nb_matches):
        #At least one of the players is human
        if not (isinstance(player1, Human) or isinstance(player2, Human)):
            raise Exception("At least one player should be human.")
        
        #Initialisation of model and view
        self.model = GameModel(nb_matches, player1, player2)
        self.view = GameView(self)

        #If AI is first to play, we make him play straight away
        if not isinstance(self.model.get_current_player(), Human):
            self.handle_ai_move()

        self.start()

    def start(self):
        self.view.mainloop()

    def get_nb_matches(self):
        return self.model.nb
    
    def get_status_message(self):
        if self.model.is_game_over():
            winner = self.model.get_winner()
            return f"Game has concluded! {winner.name} won!"
        
        current = self.model.get_current_player()
        return f"It is {current.name}'s turn."
    
    def reset_game(self):
        self.model.reset()
        self.view.reset()
        self.view.update_view()

        #AI plays straight away if he is first after reset
        if not isinstance(self.model.get_current_player(), Human):
            self.handle_ai_move()

    def handle_human_move(self, action):
        current_player = self.model.get_current_player()

        if isinstance(current_player, Human):
            self.model.step(action)

            if self.model.is_game_over():
                self.handle_end_game()
            else:
                self.model.switch_player()
                if not isinstance(self.model.get_current_player(), Human):
                    self.view.update_view()
                    self.handle_ai_move()

            self.view.update_view()

    def handle_ai_move(self):
        current_player = self.model.get_current_player()

        action = current_player.play()
        action = min(action, self.model.nb)

        self.model.step(action)

        if self.model.is_game_over():
            self.handle_end_game()
        else:
            self.model.switch_player()

        self.view.update_view()

    def handle_end_game(self):
        winner = self.model.get_winner()
        loser = self.model.get_loser()

        winner.win()
        loser.lose()

        self.view.end_game()