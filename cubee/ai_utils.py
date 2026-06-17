import multiprocessing as mp
from cubee.controller import GameController
from cubee.engine import GameEngine
from cubee.model import GameModel, Board
from cubee.player import Player, AI
from cubee.qtable_dao import QTableDAO
from cubee.qtable import QTable, SHARED_QTABLE
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
    SHARED_QTABLE.storage = delta_storage
    
    # Spin up a completely isolated game environment
    game_board = Board(5, 5)
    game_model = GameModel(game_board, *ais)
    game_engine = GameEngine(game_model)
    training_game = GameController(game_engine)

    # Calculate initial stats to find the delta for this specific worker run
    initial_stats = {ai.name: {"wins": ai.nb_wins, "losses": ai.nb_losses} for ai in ais if isinstance(ai, AI)}

    # Grind the episodes
    for _ in range(episodes):

        # Reset episodic tracking for all active AI players before restarting
        for ai in ais:
            if isinstance(ai, AI):
                ai.reset_episodic_tracking()

        training_game.restart_game(efficiency_level)
    
    # Calculate how many wins/losses happened in this worker
    stats_delta = {
        ai.name: {
            "wins": ai.nb_wins - initial_stats[ai.name]["wins"],
            "losses": ai.nb_losses - initial_stats[ai.name]["losses"]
        }
        for ai in ais if isinstance(ai, AI)
    }

    # Return only the modified states
    return {
        "qtable": delta_storage.delta,
        "stats": stats_delta
    }

def set_mode(*ais, training_mode: bool, epsilon: float = 1):
    """Set AIs in training or inference mode."""
    logger.info(f"Setting AIs in {'training' if training_mode else 'inference'} mode")
    logger.debug(f"Epsilon value set to {epsilon if training_mode else 0} for all AIs")
    for ai in ais:
        if isinstance(ai, AI):
            ai.training = training_mode
            ai.epsilon = epsilon if training_mode else 0

def training(
    *ais, epochs: int, episodes: int, epsilon: float,
    efficiency_level: int = 0, unattended: bool = False, parallel: bool = False,
    epsilon_coefficient: float = 0.95, min_epsilon: float = 0.05, epoch_summary: bool = True
) -> None:
    """
    Train the AIs during `epochs * episodes` games.
    Supports single-threaded execution or CPU-saturating multiprocessing (uses 1 thread per core).
    """
    num_workers = max(1, mp.cpu_count() // 2) if parallel else 1
    logger.debug(f"=== Training AIs on {epochs} epochs and {episodes} episodes using {num_workers} worker(s) ===")
    
    set_mode(*ais, training_mode=True, epsilon=epsilon)

    if epoch_summary:
        Player.duplicate_colors_allowed = True
        random_opponent = Player("Random_Opponent", Color.BLACK) # for evaluation
    
    # Single-thread environment setup (only used if parallel=False)
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
            
            worker_args = []
            for i in range(num_workers):
                # Distribute the remainder episodes to the last worker
                worker_episodes = episodes_per_worker + (remainder if i == num_workers - 1 else 0)
                worker_args.append((i, worker_episodes, ais, efficiency_level, SHARED_QTABLE.storage))
            
            # Spin up the CPU cores
            with mp.Pool(num_workers) as pool:
                results = pool.starmap(_worker_task, worker_args)
            
            # === Aggregate Stats from Workers ===
            for res in results:
                worker_stats = res["stats"]
                for ai in ais:
                    if isinstance(ai, AI) and ai.name in worker_stats:
                        ai.nb_wins += worker_stats[ai.name]["wins"]
                        ai.nb_losses += worker_stats[ai.name]["losses"]
            
            # === Federated Merge ===
            # Combine only the keys that were actually modified by the workers
            all_keys = set()
            for res in results:
                all_keys.update(res["qtable"].keys())
                
            original_qtable = SHARED_QTABLE.storage
                
            for state_key in all_keys:
                original_q = original_qtable.get(state_key)
                updated_qs = []
                
                for res in results:
                    local_storage = res["qtable"]

                    if state_key in local_storage:
                        updated_qs.append(local_storage[state_key])
                
                if not updated_qs:
                    continue
                elif len(updated_qs) == 1:
                    original_qtable[state_key] = updated_qs[0]
                else:
                    # Average the values for each action only among workers that changed them
                    num_actions = len(updated_qs[0])
                    avg_q = [
                        sum(q[action_index] for q in updated_qs) / len(updated_qs)
                        for action_index in range(num_actions)
                    ]
                    original_qtable[state_key] = avg_q
            
        else:
            # Fallback to standard single-threaded loop
            for _ in range(episodes):

                # Reset episodic tracking for all active AI players before restarting
                for ai in ais:
                    if isinstance(ai, AI):
                        ai.reset_episodic_tracking()

                training_game.restart_game(efficiency_level)

        # Q-Table checkpoint
        QTableDAO.save(SHARED_QTABLE, f"cubee/QTables/qtable_epoch_{epoch}.pkl")
        
        if epoch_summary:
            
            eval_games = 500
            eval_total_moves = 0
            eval_total_reward = 0
            
            print(f"\nEvaluating AI on {eval_games} games...")
            # Game Evaluation Loop (AI vs Random Player)
            ai = None
            for ai_to_evaluate in ais:
                if isinstance(ai_to_evaluate, AI):
                    ai = ai_to_evaluate
                    break
                
            # Preserve current state and training tracking counters
            saved_epsilon = ai.epsilon
            saved_training = ai.training
            saved_nb_wins = ai.nb_wins
            saved_nb_losses = ai.nb_losses
            
            # Set in training mode for pure evaluation configuration
            set_mode(ai, training_mode=False)
            
            
            
            for _ in range(eval_games):
                
                # Reset metrics for the specific isolated game transition
                ai.reset_episodic_tracking() # unnecessary probably because it's already done
                
                eval_board = Board(5, 5)
                eval_model = GameModel(eval_board, ai, random_opponent)
                eval_engine = GameEngine(eval_model)
                eval_game = GameController(eval_engine)
                
                # Suppress printing via clean efficiency interface limits
                eval_game.run(efficiency_level=3)
                    
                ai_data = eval_game.data.get(ai, None)
                eval_total_moves += ai_data["moves"] if ai_data else 0
                eval_total_reward += ai.last_reward
            
            eval_wins = ai.nb_wins - saved_nb_wins
            print(f"\n### Performance Summary ({ai.name}) ###")
            print(f"    - Epsilon:            {saved_epsilon:.4f}")
            print(f"    - Explored States:    {len(SHARED_QTABLE.storage)}")
            print(f"    - Epoch Win Rate:     {(eval_wins / eval_games) * 100:.2f}%")
            print(f"    - Avg Moves/Match:    {eval_total_moves / eval_games:.1f}")
            print(f"    - Avg Reward/Episode: {eval_total_reward / eval_games:.2f}")
            print("=========================================\n")
            
            # Re-establish parameters for subsequent training cycles
            ai.nb_wins = saved_nb_wins
            ai.nb_losses = saved_nb_losses

            # Set in training mode for pure evaluation configuration
            set_mode(ai, training_mode=True, epsilon=saved_epsilon)

        # Epsilon Decay and Human Interaction Check
        for ai in ais:
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

            #print(f"{ai.name} (AI):")
            #print(f"    - Epsilon: {ai.epsilon}")
            #print(f"    - Wins: {ai.nb_wins} | Losses: {ai.nb_losses}")

    set_mode(*ais, training_mode=False)
    logger.info("=== Training completed successfully ===")
