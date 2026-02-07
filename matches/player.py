from random import randint, choice, random

class Player():
    def __init__(self, name: str, game = None):
        self.name = name
        self.nb_wins = 0
        self.nb_losses = 0
        self.game = game

    @staticmethod
    def play():
        return randint(1, 3)
        
    @property
    def nb_games(self):
        return self.nb_wins + self.nb_losses

    def win(self):
        self.nb_wins += 1

    def lose(self):
        self.nb_losses += 1

    def __str__(self):
        return f"{self.name} has {self.nb_wins} victories and {self.nb_losses} losses in {self.nb_games} games!"
    
class Human(Player):
    def play(self):
        while True:
            try:
                nb_matches_to_remove = int(input("Enter the number of matches you would like to remove (1, 2 or 3): "))

                if 0 < nb_matches_to_remove < 4:
                    return nb_matches_to_remove
                
                print("Invalid Entry!")
            except ValueError:
                print("Invalid Entry!")

class AI(Player):
    def __init__(self, name, game=None, epsilon = 0.9, lr = 0.01, gamma = 1):
        super().__init__(name, game)
        self.epsilon = epsilon
        self.lr = lr
        self.gamma = gamma
        self.history = []
        self.previous_state = None
        self.values = {
            "win": 1,
            "lose": -1
        }

    def exploit(self):
        current_matches = self.game.get_remaining_matches()

        actions = [a for a in [1, 2, 3] if a <= current_matches]

        evaluations = []

        for action in actions:
            next_state = current_matches - action

            self.values.setdefault(next_state, 0)

            evaluations.append((action, self.values[next_state]))

        min_value = min(value for (_, value) in evaluations)

        best_actions = [action for (action, value) in evaluations if value == min_value]

        return choice(best_actions)

    def play(self):
        current_state = self.game.get_remaining_matches()

        if self.previous_state is not None:
            self.history.append((self.previous_state, current_state))

        self.previous_state = current_state

        if random() < self.epsilon:
            valid_actions = [a for a in [1,2,3] if a <= current_state]
            return choice(valid_actions)
        
        return self.exploit()

    def win(self):
        super().win()

        if self.previous_state is not None:
            self.history.append((self.previous_state, "win"))

            self.previous_state = None

    def lose(self):
        super().lose()

        if self.previous_state is not None:
            self.history.append((self.previous_state, "lose"))

            self.previous_state = None

    def train(self):
        for prev_state, next_state in reversed(self.history):
            self.values.setdefault(prev_state, 0)
            self.values.setdefault(next_state, 0)
            self.values[prev_state] += self.lr * (self.values[next_state] - self.values[prev_state])

        self.history = []


    def next_epsilon(self, coefficient = 0.95, minimum_eps = 0.05):
        self.epsilon *= coefficient
        if self.epsilon < minimum_eps:
            self.epsilon = minimum_eps