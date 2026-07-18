import sys
import os

_project_dir = os.path.dirname(os.path.abspath(__file__))
_game_env = os.path.join(_project_dir, "game-enviroment")
if _game_env not in sys.path:
    sys.path.insert(0, _game_env)

from main import main

if __name__ == "__main__":
    main()
