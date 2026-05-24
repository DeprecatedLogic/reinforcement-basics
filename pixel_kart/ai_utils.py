import multiprocessing as mp
from pixel_kart.controller import GameController
from pixel_kart.engine import GameEngine
from pixel_kart.model import GameModel, Board
from pixel_kart import circuit_dao as CircuitDAO
from pixel_kart.player import Player, AI
from pixel_kart.qtable_dao import QTableDAO
from pixel_kart.qtable import QTable, SHARED_QTABLE
import logging

logger = logging.getLogger(__name__)

def _worker_task(worker_id: int, episodes: int, ais: tuple, circuit_name: str, laps: int, efficiency_level: int, current_qtable_state: dict) -> dict:
    """
    Isolated worker process that runs a subset of episodes at maximum speed
    using a local, independent copy of the Q-Table.
    """
    # Point the worker's local SHARED_QTABLE to the provided state copy
    SHARED_QTABLE.storage = current_qtable_state.copy()
    
    # Spin up a completely isolated game environment
    grid = CircuitDAO.get_by_name(circuit_name)
    board = Board.load(grid)
    model = GameModel(board, *ais, laps_required=laps)
    engine = GameEngine(model)
    training_game = GameController(engine)

    # Calculate initial stats to find the delta for this specific worker run
    initial_stats = {ai.name: {"wins": ai.nb_wins, "losses": ai.nb_losses} for ai in ais if isinstance(ai, AI)}

    # Grind the episodes
    for _ in range(episodes):
        training_game.restart_game(efficiency_level)
    
    # Calculate how many wins/losses happened in this worker
    stats_delta = {
        ai.name: {
            "wins": ai.nb_wins - initial_stats[ai.name]["wins"],
            "losses": ai.nb_losses - initial_stats[ai.name]["losses"]
        }
        for ai in ais if isinstance(ai, AI)
    }

    # Return the locally trained brain and the stats
    return {
        "qtable": SHARED_QTABLE.storage,
        "stats": stats_delta
    }

def set_mode(*ais, training_mode: bool, epsilon: float = 1):
    """Set AIs in training or inference mode."""
    logger.info(f"Setting AIs in {'training' if training_mode else 'inference'} mode")
    logger.debug(f"Epsilon value set to {epsilon} for all AIs")
    for ai in ais:
        if isinstance(ai, AI):
            ai.training = training_mode
            ai.epsilon = epsilon

def training(*ais, epochs: int, episodes: int, epsilon: float, circuit_name: str, laps: int = 1, efficiency_level: int = 0, unattended: bool = False, parallel: bool = False) -> None:
    """
    Train the AIs during `epochs * episodes` games.
    Supports single-threaded execution or CPU-saturating multiprocessing (uses 1 thread per core).
    """
    num_workers = max(1, mp.cpu_count() // 2) if parallel else 1
    logger.debug(f"=== Training AIs on {epochs} epochs and {episodes} episodes using {num_workers} worker(s) ===")
    
    set_mode(*ais, training_mode=True, epsilon=epsilon)
    continue_training = []

    # Single-thread environment setup (only used if parallel=False)
    if not parallel:
        grid = CircuitDAO.get_by_name(circuit_name)
        board = Board.load(grid)
        model = GameModel(board, *ais, laps_required=laps)
        engine = GameEngine(model)
        training_game = GameController(engine)

    logger.info("Starting AI training")
    for epoch in range(epochs):
        logger.info(f"Epoch {epoch}")
        print(f"=== Epoch {epoch} ===")
        
        if parallel and num_workers > 1:
            episodes_per_worker = episodes // num_workers
            remainder = episodes % num_workers
            
            worker_args = []
            for i in range(num_workers):
                # Distribute the remainder episodes to the last worker
                worker_episodes = episodes_per_worker + (remainder if i == num_workers - 1 else 0)
                worker_args.append((i, worker_episodes, ais, circuit_name, laps, efficiency_level, SHARED_QTABLE.storage))
            
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
            # Combine the Q-tables from all workers by averaging their learned Q-values\
            # (if worker never encountered that state, it's not taken into account when calculating the average)
            merged_storage = {}
            all_keys = set()
            for res in results:
                local_storage = res["qtable"]
                all_keys.update(local_storage.keys())
                
            original_qtable = SHARED_QTABLE.storage
                
            for state_key in all_keys:
                original_q = original_qtable.get(state_key)
                updated_qs = []
                
                for res in results:
                    local_storage = res["qtable"]

                    if state_key in local_storage:
                        local_q = local_storage[state_key]
                        # Only collect Q-values from workers that actually modified this state
                        if original_q is None or local_q != original_q:
                            updated_qs.append(local_q)
                
                if not updated_qs:
                    merged_storage[state_key] = original_q
                elif len(updated_qs) == 1:
                    merged_storage[state_key] = updated_qs[0]
                else:
                    # Average the values for each action only among workers that changed them
                    num_actions = len(updated_qs[0])
                    avg_q = [
                        sum(q[action_idx] for q in updated_qs) / len(updated_qs)
                        for action_idx in range(num_actions)
                    ]
                    merged_storage[state_key] = avg_q
                    
            # Overwrite the master brain with the merged results
            SHARED_QTABLE.storage = merged_storage
            
        else:
            # Fallback to standard single-threaded loop
            for episode in range(episodes):
                training_game.restart_game(efficiency_level)

        # Q-Table checkpoint
        QTableDAO.save(SHARED_QTABLE, f"pixel_kart/QTables/qtable_epoch_{epoch}.pkl")
        
        # Epsilon Decay and Human Interaction Check
        for ai in ais:
            if not isinstance(ai, AI):
                continue

            ai.next_epsilon()

            if ai.epsilon == 0.05 and ai not in continue_training:
                logger.info(f"{ai.name} (AI) epsilon reached the minimum value {ai.epsilon}")

                if unattended:
                    logger.info("Unattended mode active. Continuing training automatically")
                    continue_training.append(ai)
                else:
                    user_input = input(f"{ai.name} epsilon hit minimum. Stop training? (y/n) ")
                    if user_input.strip().lower() in ('y', "yes"):
                        logger.debug(f"Training stopped by user (input={user_input})")
                        set_mode(*ais, training_mode=False, epsilon=0)
                        return 
                    continue_training.append(ai)

            print(f"{ai.name} (AI):")
            print(f"    - Epsilon: {ai.epsilon}")
            print(f"    - Wins: {ai.nb_wins} | Losses: {ai.nb_losses}")

    set_mode(*ais, training_mode=False, epsilon=0)
    logger.info("=== Training completed successfully ===")