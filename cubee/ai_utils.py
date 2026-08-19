import multiprocessing as mp
from cubee.controller import GameController
from cubee.engine import GameEngine
from cubee.model import GameModel, Board
from cubee.player import Player, AI
from cubee.qtable_dao import QTableDAO
from cubee.colors import Color

import logging
logger = logging.getLogger(__name__)

class DeltaStorage:
    def __init__(self, base_dict: dict) -> None:
        self.base_dict = base_dict
        self.delta = {}

    def setdefault(self, key, default):
        if key in self.delta:
            return self.delta[key]
        if key in self.base_dict:
            # Copy to avoid mutating the shared base process memory
            self.delta[key] = list(self.base_dict[key])
            return self.delta[key]
        self.delta[key] = default
        return self.delta[key]

    def __getitem__(self, key):
        if key in self.delta:
            return self.delta[key]
        self.delta[key] = list(self.base_dict[key])
        return self.delta[key]

def _worker_task(worker_id: int, episodes: int, ais: tuple, efficiency_level: int, current_qtable_state: dict) -> dict:
    """
    Isolated worker process that runs a subset of episodes.

    Args:
        worker_id (int): _description_
        episodes (int): _description_
        ais (tuple): _description_
        efficiency_level (int): _description_
        current_qtable_state (dict): _description_

    Returns:
        dict: _description_
    """
    # Track only changes instead of copying the whole table
    delta_storage = DeltaStorage(current_qtable_state)
    for ai in ais:
        if isinstance(ai, AI):
            qtable_id = id(ai.qtable)
            if qtable_id not in delta_storages:
                base_dict = current_qtables_state.get(qtable_id, {})
                delta_storages[qtable_id] = DeltaStorage(base_dict)
            ai.qtable.storage = delta_storages[qtable_id]

    # Spin up a completely isolated game environment
    game_board = Board(5, 5)
    game_model = GameModel(game_board, *ais)
    game_engine = GameEngine(game_model)
    training_game = GameController(game_engine)

    unique_ais = list(dict.fromkeys(ais))
    # Calculate initial stats to find the delta for this specific worker run
    initial_stats = {id(ai): {"wins": ai.nb_wins, "losses": ai.nb_losses} for ai in unique_ais if isinstance(ai, AI)}

    # Grind the episodes
    for _ in range(episodes):
        # Reset episodic tracking for all active AI players before restarting
        for ai in unique_ais:
            if isinstance(ai, AI):
                ai.reset_episodic_tracking()

        training_game.restart_game(efficiency_level)
    
    # Calculate how many wins/losses happened in this worker
    stats_delta = {
        ai.name: {
            "wins": ai.nb_wins - initial_stats[id(ai)]["wins"],
            "losses": ai.nb_losses - initial_stats[id(ai)]["losses"]
        }
        for ai in unique_ais if isinstance(ai, AI)
    }

    # Return only the modified states
    return {
        "qtables": {qtable_id: delta.delta for qtable_id, delta in delta_storages.items()},
        "stats": stats_delta
    }

def set_mode(*ais, training_mode: bool, epsilon: float = 1) -> None:
    """Set AIs in training or inference mode."""
    logger.info(f"Setting AIs in {'training' if training_mode else 'inference'} mode")
    logger.debug(f"Epsilon value set to {epsilon if training_mode else 0} for all AIs")
    for ai in dict.fromkeys(ais):
        if isinstance(ai, AI):
            ai.training = training_mode
            ai.epsilon = epsilon if training_mode else 0

def test_ais(p1: Player, p2: Player, nb_matches: int = 500, efficiency_level: int = 3) -> None:
    """
    Evaluates two players over a given number of matches and prints performance summary.

    Args:
        p1 (Player): _description_
        p2 (Player): _description_
        nb_matches (int): _description_
        efficiency_level (int): _description_
    """
    p1_training_mode = p1.training if isinstance(p1, AI) else None
    p2_training_mode = p2.training if isinstance(p2, AI) else None
    set_mode(p1, p2, training_mode=False)

    p1_moves = 0
    p1_rewards = 0
    p2_moves = 0
    p2_rewards = 0

    p1_wins_start = p1.nb_wins if hasattr(p1, 'nb_wins') else 0
    p2_wins_start = p2.nb_wins if hasattr(p2, 'nb_wins') else 0

    game_board = Board(5, 5)
    game_model = GameModel(game_board, p1, p2)
    game_engine = GameEngine(game_model)
    test_game = GameController(game_engine)

    print("\n=========================================")
    print(f"  Testing: {p1.name} vs {p2.name} ({nb_matches} matches)")
    print("=========================================\n")

    unique_players = list(dict.fromkeys([p1, p2]))

    for _ in range(nb_matches):
        for p in unique_players:
            if isinstance(p, AI):
                p.reset_episodic_tracking()

        test_game.restart_game(efficiency_level=efficiency_level)

        p1_data = test_game.data.get(p1, None)
        p2_data = test_game.data.get(p2, None)

        if p1_data:
            p1_moves += p1_data.get("moves", 0)
        if p2_data:
            p2_moves += p2_data.get("moves", 0)

        if hasattr(p1, 'last_reward'):
            p1_rewards += p1.last_reward
        if hasattr(p2, 'last_reward'):
            p2_rewards += p2.last_reward

    p1_wins = (p1.nb_wins - p1_wins_start) if hasattr(p1, 'nb_wins') else 0
    p2_wins = (p2.nb_wins - p2_wins_start) if hasattr(p2, 'nb_wins') else 0
    draws = nb_matches - (p1_wins + p2_wins)

    for p, wins, moves, rewards in [
        (p1, p1_wins, p1_moves, p1_rewards),
        (p2, p2_wins, p2_moves, p2_rewards)
    ]:
        print(f"### Performance Summary ({p.name}) ###")
        if isinstance(p, AI):
            print(f"    - Epsilon:            {p.epsilon:.4f}")
            print(f"    - Explored States:    {len(p.qtable.storage)}")
        print(f"    - Win Rate:           {(wins / nb_matches) * 100:.2f}% ({wins}/{nb_matches})")
        print(f"    - Avg Moves/Match:    {moves / nb_matches:.1f}")
        if isinstance(p, AI):
            print(f"    - Avg Reward/Episode: {rewards / nb_matches:.2f}")
        print("-----------------------------------------")
    print(f"    - Draws:              {draws} ({(draws / nb_matches) * 100:.2f}%)")
    print("=========================================\n")

    if p1_training_mode:
        set_mode(p1, training_mode=p1_training_mode)
    if p2_training_mode:
        set_mode(p2, training_mode=p2_training_mode)

def training(
    *ais, epochs: int, episodes: int, epsilon: float,
    efficiency_level: int = 0, unattended: bool = False, parallel: bool = False,
    epsilon_coefficient: float = 0.95, min_epsilon: float = 0.05,
    gamma: float = 0.95, learning_rate: float = 0.1, opponent: str = "AI",
    skip_checkpoints: bool = False, epoch_summary: bool = True, shared_qtable: bool = False
) -> None:
    """
    Train the AIs during `epochs * episodes` games.
    Supports single-threaded execution or CPU-saturating multiprocessing (uses 1 thread per core).

    Args:
        *ais: _description_
        epochs (int): _description_
        episodes (int): _description_
        epsilon (float): _description_
        efficiency_level (int): _description_
        unattended (bool): _description_
        parallel (bool): _description_
        epsilon_coefficient (float): _description_
        min_epsilon (float): _description_
        gamma (float): _description_
        learning_rate (float): _description_
        opponent (str): _description_
        skip_checkpoints (bool): _description_
        epoch_summary (bool): _description_
        shared_qtable (bool): _description_
    """
    if shared_qtable:
        first_qtable = next((ai.qtable for ai in ais if isinstance(ai, AI)), None)
        if first_qtable:
            for ai in ais:
                if isinstance(ai, AI):
                    ai.qtable = first_qtable

    unique_ais = list(dict.fromkeys(ais))
    num_workers = max(1, mp.cpu_count() // 2) if parallel else 1
    logger.debug(f"=== Training AIs on {epochs} epochs and {episodes} episodes using {num_workers} worker(s) ===")

    set_mode(*ais, training_mode=True, epsilon=epsilon)

    if epoch_summary:
        Player.duplicate_colors_allowed = True
        random_opponent = Player("Random_Opponent", Color.BLACK)

    if not parallel:
        game_board = Board(5, 5)
        game_model = GameModel(game_board, *ais)
        game_engine = GameEngine(game_model)
        training_game = GameController(game_engine)

    logger.info("Starting AI training")
    continue_training = []

    for epoch in range(epochs):
        logger.info(f"Epoch {epoch}")
        print(f"============= Epoch {epoch} =============")

        print("\nTraining...")
        if parallel and num_workers > 1:
            episodes_per_worker = episodes // num_workers
            remainder = episodes % num_workers

            current_qtables_state = {id(ai.qtable): ai.qtable.storage for ai in unique_ais if isinstance(ai, AI)}

            worker_args = []
            for i in range(num_workers):
                worker_episodes = episodes_per_worker + (remainder if i == num_workers - 1 else 0)
                worker_args.append((i, worker_episodes, ais, efficiency_level, current_qtables_state))

            with mp.Pool(num_workers) as pool:
                results = pool.starmap(_worker_task, worker_args)

            for res in results:
                worker_stats = res["stats"]
                for ai in unique_ais:
                    if isinstance(ai, AI) and ai.name in worker_stats:
                        ai.nb_wins += worker_stats[ai.name]["wins"]
                        ai.nb_losses += worker_stats[ai.name]["losses"]

            unique_qtables = {id(ai.qtable): ai.qtable for ai in unique_ais if isinstance(ai, AI)}

            for qtable_id, qtable_obj in unique_qtables.items():
                original_qtable = qtable_obj.storage

                all_keys = set()
                for res in results:
                    all_keys.update(res["qtables"].get(qtable_id, {}).keys())

                for state_key in all_keys:
                    updated_qs = [res["qtables"][qtable_id][state_key] for res in results if state_key in res["qtables"].get(qtable_id, {})]

                    if not updated_qs:
                        continue
                    elif len(updated_qs) == 1:
                        original_qtable[state_key] = updated_qs[0]
                    else:
                        num_actions = len(updated_qs[0])
                        avg_q = [
                            sum(q[action_index] for q in updated_qs) / len(updated_qs)
                            for action_index in range(num_actions)
                        ]
                        original_qtable[state_key] = avg_q

        else:
            for _ in range(episodes):
                for ai in unique_ais:
                    if isinstance(ai, AI):
                        ai.reset_episodic_tracking()

                training_game.restart_game(efficiency_level)

        if not skip_checkpoints or epoch == epochs - 1:
            folder_name = '-'.join((
                f"epochs_{epochs}",
                f"eps_{episodes}",
                f"gamma_{gamma}",
                f"lr_{learning_rate}",
                f"epsilon_{epsilon}",
                f"epscoeff_{epsilon_coefficient}",
                f"mineps_{min_epsilon}"
            ))
            saved_qtables = set()
            for ai in unique_ais:
                if isinstance(ai, AI):
                    qtable_id = id(ai.qtable)
                    if qtable_id not in saved_qtables:
                        QTableDAO.save(ai.qtable, f"cubee/QTables/opponent_{opponent}/{folder_name}/{'_'.join(ai.name.split())}_epoch_{epoch}.pkl")
                        saved_qtables.add(qtable_id)

        if epoch_summary:
            eval_games = 500
            ai = next((ai_to_eval for ai_to_eval in unique_ais if isinstance(ai_to_eval, AI)), None)

            if ai:
                saved_epsilon = ai.epsilon
                saved_nb_wins = ai.nb_wins
                saved_nb_losses = ai.nb_losses

                test_ais(ai, random_opponent, nb_matches=eval_games, efficiency_level=3)

                ai.nb_wins = saved_nb_wins
                ai.nb_losses = saved_nb_losses
                set_mode(ai, training_mode=True, epsilon=saved_epsilon)

        for ai in unique_ais:
            if not isinstance(ai, AI):
                continue

            ai.next_epsilon(coefficient=epsilon_coefficient, minimum_eps=min_epsilon)

            if ai.epsilon == min_epsilon and ai not in continue_training:
                logger.info(f"{ai.name} (AI) epsilon reached the minimum value {ai.epsilon}")

                if unattended:
                    logger.info("Unattended mode active. Continuing training automatically")
                    continue_training.append(ai)
                else:
                    user_input = input(f"{ai.name} epsilon hit minimum value. Stop training? (y/n) ")
                    if user_input.strip().lower() in ('y', "yes"):
                        logger.debug(f"Training stopped by user (input={user_input})")
                        set_mode(*ais, training_mode=False, epsilon=0)
                        return
                    continue_training.append(ai)

    set_mode(*ais, training_mode=False)
    logger.info("=== Training completed successfully ===")
