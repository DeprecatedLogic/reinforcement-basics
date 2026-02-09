from matches.player import Player, Human, AI
from matches.game_controller import GameController
from matches.game_model import GameModel

def training(ai1, ai2, nb_games, nb_epsilon, nb_matches = 12):
    # Train the AIs @ai1 and @ai2 during @nb_games games
    # epsilon decrease every @nb_epsilon games
    training_game = GameModel(nb_matches, ai1, ai2, displayable = False)
    for i in range(0, nb_games):
        if i % nb_epsilon == 0:
            if type(ai1)==AI : ai1.next_epsilon()
            if type(ai2)==AI : ai2.next_epsilon()

        training_game.play()
        if type(ai1)==AI : ai1.train()
        if type(ai2)==AI : ai2.train()

        training_game.reset()

def compare_ai(*ais):
    # Print a comparison between the @ais
    names = f"{'':4}"
    stats1 = f"{'':4}"
    stats2 = f"{'':4}"

    for ai in ais :
        names += f"{ai.name:^15}"
        stats1 += f"{str(ai.nb_wins)+'/'+str(ai.nb_games):^15}"
        stats2 += f"{f'{ai.nb_wins/ai.nb_games*100:4.4}'+'%':^15}"

    print(names)
    print(stats1)
    print(stats2)
    print(f"{'-'*4}{'-'*len(ais)*15}")

    all_v_dict = {key : [ai.values.get(key,0) for ai in ais] for key in ais[0].values.keys()}
    sorted_v = lambda v_dict : sorted(filter(lambda x : type(x[0])==int ,v_dict.items()))
    for state, values in sorted_v(all_v_dict):
        print(f"{state:2} :", end='')
        for value in values:
            print(f"{value:^15.3}", end='')
        print()

if __name__ == "__main__":
    p1 = Human("Gevin")
    p2 = Player("Player2")
    alice = AI("Alice")
    bobby = AI("Bobby")
    randy = AI("Randy")
    
    bobby.epsilon = 1
    training(alice, bobby, 100000, 1000, 21)
    training(p2, randy, 100000, 1, 21)
    bobby.reset_stats()
    randy.reset_stats()

    randy.epsilon = 0
    bobby.epsilon = 0

    for i in range(100):
        game1 = GameModel(21, bobby, randy).play()
    
    #game = GameController(p1, bobby, 21)
    compare_ai(alice, bobby, randy)