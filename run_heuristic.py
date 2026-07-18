import sys
import os

_project_dir = os.path.dirname(os.path.abspath(__file__))
_game_env = os.path.join(_project_dir, "game-enviroment")
if _game_env not in sys.path:
    sys.path.insert(0, _game_env)

from agents.heuristic_goal.heuristic_agent import main, main_trained
from agents.heuristic_goal.replay_buffer import list_runs

if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "--trained":
        main_trained(sys.argv[2])
    elif len(sys.argv) == 2 and sys.argv[1] == "--list":
        runs = list_runs()
        if runs:
            print("Runs salvos:")
            for r in runs:
                ts = r["timestamp"][:19] if r["timestamp"] else "?"
                print(
                    f"  run_{r['id']:03d}  {ts}"
                    f"  steps={r['steps']}  thrusts={r['thrusts']}"
                    f"  fuel={r['fuel_used']:.0f}  reward={r['reward']:.0f}"
                )
        else:
            print("Nenhum run salvo ainda.")
    else:
        main()
