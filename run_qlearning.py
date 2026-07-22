"""
run_qlearning.py — Entrada unificada para o agente Q-Learning Tabular.

Uso:
  python run_qlearning.py                    # modo watch (padrao, 1 episodio)
  python run_qlearning.py --train            # treino headless (80000 episodios)
  python run_qlearning.py --train --eps 1000 # treino com N episodios
  python run_qlearning.py --watch            # assiste o agente treinado
  python run_qlearning.py --watch --episodios 5  # assiste N episodios
  python run_qlearning.py --list             # lista checkpoints salvos
"""

import sys
import os

_project_dir = os.path.dirname(os.path.abspath(__file__))
_game_env = os.path.join(_project_dir, "game-enviroment")
if _game_env not in sys.path:
    sys.path.insert(0, _game_env)

from agents.q_learning.treinador import treinar, assistir, listar


def print_help():
    print("Uso: python run_qlearning.py [modo] [opcoes]")
    print()
    print("Modos:")
    print("  (sem argumentos)       Assiste o agente treinado (1 episodio)")
    print("  --train                Treino headless (80000 episodios)")
    print("  --train --eps N        Treino com N episodios")
    print("  --watch                Assiste o agente treinado")
    print("  --watch --episodios N  Assiste N episodios")
    print("  --list                 Listar checkpoints salvos")


def main():
    args = sys.argv[1:]

    if "--help" in args or "-h" in args:
        print_help()
        return

    if "--list" in args:
        listar()
        return

    if "--train" in args:
        n_episodios = 80000
        for i, arg in enumerate(args):
            if arg == "--eps" and i + 1 < len(args):
                n_episodios = int(args[i + 1])
        treinar(n_episodios=n_episodios)
        return

    if "--watch" in args:
        n_episodios = 1
        for i, arg in enumerate(args):
            if arg == "--episodios" and i + 1 < len(args):
                n_episodios = int(args[i + 1])
        assistir(episodios=n_episodios)
        return

    assistir(episodios=1)


if __name__ == "__main__":
    main()
