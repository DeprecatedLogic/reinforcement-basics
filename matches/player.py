from random import randint, choice, random
import json

class Player():
    """Base class representing a participant in the game. It can be a human or an AI."""
    def __init__(self, name: str, game = None):
        """
        Initialize a new player.

        Args:
            name: The player's display name
            game: Optional reference to the active GameModel instance
        """
        self.name = name
        self.nb_wins = 0
        self.nb_losses = 0
        self.game = game

    @staticmethod
    def play() -> int:
        """
        Determine how many matches the player wants to remove.

        Returns:
            An integer between 1 and 3 (inclusive) representing matches to take
        """
        return randint(1, 3)
        
    @property
    def nb_games(self) -> int:
        """Return the total number of games played by the player."""
        return self.nb_wins + self.nb_losses

    def win(self) -> None:
        """Increment the player's win counter."""
        self.nb_wins += 1

    def lose(self) -> None:
        """Increment the player's loss counter."""
        self.nb_losses += 1

    def reset_stats(self) -> None:
        """Reset this player's win and loss counters to zero."""
        self.nb_wins = 0
        self.nb_losses = 0

    def __str__(self) -> str:
        """Return a string representation of the player's statistics."""
        return f"{self.name} has {self.nb_wins} victories and {self.nb_losses} losses in {self.nb_games} games!"
    
class Human(Player):
    """Player controlled by a human user via console input."""
    def play(self) -> int:
        """
        Prompt the human player for the number of matches to remove.

        Returns:
            Valid number of matches to remove (1, 2, or 3)
        """
        while True:
            try:
                nb_matches_to_remove = int(input("Enter the number of matches you would like to remove (1, 2 or 3): "))

                if 0 < nb_matches_to_remove < 4:
                    return nb_matches_to_remove
                
                print("Invalid Entry!")
            except ValueError:
                print("Invalid Entry!")

class AI(Player):
    """
    Reinforcement learning agent that learns to play the game by updating
    its value estimates based on game outcomes.
    """
    def __init__(self, name, game=None, epsilon = 0.9, lr = 0.01, gamma = 1):
        """
        Initialize the learning agent.

        Args:
            name: Name of the AI player
            game: Reference to the current GameModel (optional at init)
            epsilon: Initial exploration probability (0.0-1.0)
            lr: Learning rate for value function updates
            gamma: Discount factor (typically 1.0 for undiscounted terminal games)
        """
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

    def exploit(self) -> int:
        """
        Select the currently best-known action (greedy policy).

        Returns:
            Action (1, 2, or 3) with the lowest estimated value for the opponent
        """
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

    def play(self) -> int:
        """
        Choose an action using epsilon-greedy policy.

        Returns:
            Number of matches to remove (1-3)
        """
        current_state = self.game.get_remaining_matches()

        if self.previous_state is not None:
            self.history.append((self.previous_state, current_state))

        self.previous_state = current_state

        if random() < self.epsilon:
            valid_actions = [a for a in [1,2,3] if a <= current_state]
            return choice(valid_actions)
        
        return self.exploit()

    def win(self) -> None:
        """Record a win and store transition to winning terminal state."""
        super().win()

        if self.previous_state is not None:
            self.history.append((self.previous_state, "win"))

            self.previous_state = None

    def lose(self) -> None:
        """Record a loss and store transition to losing terminal state."""
        super().lose()

        if self.previous_state is not None:
            self.history.append((self.previous_state, "lose"))

            self.previous_state = None

    def train(self) -> None:
        """
        Perform one backward pass of temporal-difference learning over the episode.
        Updates value estimates toward observed outcomes.
        """
        for prev_state, next_state in reversed(self.history):
            self.values.setdefault(prev_state, 0)
            self.values.setdefault(next_state, 0)
            self.values[prev_state] += self.lr * (self.values[next_state] - self.values[prev_state])

        self.history = []


    def next_epsilon(self, coefficient = 0.1, minimum_eps = 0.05) -> None:
        """
        Reduce the exploration rate (epsilon decay).

        Args:
            coefficient: Multiplicative decay factor (should be < 1)
            minimum_eps: Floor value below which epsilon will not decrease
        """
        self.epsilon *= coefficient
        if self.epsilon < minimum_eps:
            self.epsilon = minimum_eps

    def download(self, filename: str) -> None:
        """
        Serialize the AI's key learning parameters and value function to a JSON file.
        
        Args:
            filename: Path to the file where the data will be saved
        """
        if not filename.endswith(".json"):
            filename += ".json"

        #Convert dict keys to str for json compatibility
        values_str = {str(k): v for k, v in self.values.items()}
        
        data = {
            'epsilon': self.epsilon,
            'lr': self.lr,
            'gamma': self.gamma,
            'values': values_str
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)

    def load(self, filename: str) -> None:
        """
        Deserialize the AI's key learning parameters and value function from a JSON file.
        
        Args:
            filename: Path to the file from which the data will be loaded
        """
        with open(filename, 'r') as f:
            data = json.load(f)
        
        self.epsilon = data['epsilon']
        self.lr = data['lr']
        self.gamma = data['gamma']
        
        #Reconstruct values dict with original key types
        values_str = data['values']
        self.values = {}
        for k_str, v in values_str.items():
            if k_str in ['win', 'lose']:
                k = k_str
            else:
                k = int(k_str)
            self.values[k] = v