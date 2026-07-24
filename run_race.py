"""
run_race.py — Corrida dos 3 Agentes Treinados.

Carrega os melhores modelos de cada agente (heuristico, Q-Learning, genetico)
e os coloca para correr simultaneamente no mesmo ambiente.
Cada nave tem seus proprios checkpoints coloridos.

Uso:
  python run_race.py

Requer que todos os 3 agentes tenham sido treinados:
  - Heuristico: pelo menos um run salvo (run_heuristic.py)
  - Q-Learning: Q-table treinada (run_qlearning.py --train)
  - Genetico: melhor cerebro (run_genetic.py --train)
"""

import sys
import os

_project_dir = os.path.dirname(os.path.abspath(__file__))
_game_env = os.path.join(_project_dir, "game-enviroment")
if _game_env not in sys.path:
    sys.path.insert(0, _game_env)

import pygame
from race_env import RaceEnv
from orbital_env import OrbitalEnv

from agents.heuristic_goal.replay_buffer import load_run, list_runs
from agents.heuristic_goal.auto_pilot import AutoPilot

from agents.q_learning.discretizer import DiscretizadorEstado
from agents.q_learning.agent import AgenteQLearning

from agents.genetic.treinador import TreinadorGenetico
from agents.genetic.ship import CerebroNave


MAX_STEPS = 2000


class HeuristicController:
    def __init__(self, run_data):
        self.actions = run_data.get("actions", [])
        self.segments = run_data["segments"]
        self.has_actions = len(self.actions) > 0
        self.action_idx = 0
        self.autopilot = None
        self.seg_idx = 0

    def get_action(self, obs, planets):
        if self.has_actions:
            if self.action_idx < len(self.actions):
                action = self.actions[self.action_idx]
                self.action_idx += 1
                return action
            return 0

        if self.seg_idx >= len(self.segments):
            return 0

        if self.autopilot is None:
            seg = self.segments[self.seg_idx]
            path = [list(wp) for wp in seg.get("waypoints", [])]
            self.autopilot = AutoPilot(path, planets)

        if not self.autopilot.has_path():
            self.seg_idx += 1
            self.autopilot = None
            return 0

        return self.autopilot.get_action(obs)

    def on_checkpoint_collected(self):
        self.autopilot = None


def check_models():
    errors = []
    models = {}

    runs = list_runs()
    if not runs:
        errors.append("Heuristico: nenhum run salvo. Execute: python run_heuristic.py")
    else:
        models["heuristic"] = load_run("latest")

    checkpoint_dir = os.path.join(
        _project_dir, "game-enviroment", "agents", "q_learning", "checkpoints"
    )
    qtable_path = os.path.join(checkpoint_dir, "q_table_odisseia.pkl")
    if not os.path.exists(qtable_path):
        errors.append("Q-Learning: Q-table nao encontrada. Execute: python run_qlearning.py --train")
    else:
        models["qlearning"] = qtable_path

    gen_checkpoint_dir = os.path.join(
        _project_dir, "game-enviroment", "agents", "genetic", "checkpoints"
    )
    gen_path = os.path.join(gen_checkpoint_dir, "best.pkl")
    gen_data = TreinadorGenetico.carregar()
    if gen_data is None:
        errors.append("Genetico: best.pkl nao encontrado. Execute: python run_genetic.py --train")
    else:
        models["genetic"] = gen_data

    if errors:
        print("\n=== MODELOS NAO TREINADOS ===")
        for e in errors:
            print(f"  - {e}")
        print()
        return None

    return models


def main():
    models = check_models()
    if models is None:
        return

    print("=" * 55)
    print("  ODISSEIA ORBITAL — Corrida dos Agentes")
    print("=" * 55)
    print(f"  Heuristico : run mais recente carregado")
    print(f"  Q-Learning : Q-table carregada")
    print(f"  Genetico   : gen {models['genetic']['generation']} | fit={models['genetic']['fitness']:.0f}")
    print("-" * 55)

    heuristic_ctrl = HeuristicController(models["heuristic"])

    ql_agent = AgenteQLearning(n_acoes=5)
    ql_agent.carregar(models["qlearning"])
    ql_agent.epsilon = 0.0

    gen_cerebro = CerebroNave()
    gen_cerebro.definir_cromossomo(models["genetic"]["cromossomo"])

    env = RaceEnv(render_mode="human")

    ql_disc = DiscretizadorEstado(
        checkpoints=env.ships[1]["checkpoints"],
        posicao_estacao=env.station_pos,
        planetas=env.planets,
    )

    obs_list = env.reset()

    running = True
    all_done = False
    leaderboard_shown = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    obs_list = env.reset()
                    heuristic_ctrl = HeuristicController(models["heuristic"])
                    all_done = False
                    leaderboard_shown = False

        all_done = all(s["done"] for s in env.ships)

        if all_done:
            if not leaderboard_shown:
                ranked = sorted(env.ships, key=lambda s: s["steps"])
                print("-" * 55)
                print("  CORRIDA FINALIZADA!")
                for i, s in enumerate(ranked):
                    status = s["status"].upper()
                    print(f"  {i + 1}. {s['name']:12s} {s['steps']:4d} steps  [{status}]")
                print("-" * 55)
                leaderboard_shown = True
            env.render()
            continue

        if not all_done:
            actions = []

            if not env.ships[0]["done"]:
                action_heur = heuristic_ctrl.get_action(
                    obs_list[0], env.planets
                )
            else:
                action_heur = 0
            actions.append(action_heur)

            if not env.ships[1]["done"]:
                estado = ql_disc.discretizar(obs_list[1])
                action_ql = ql_agent.selecionar_acao(estado)
            else:
                action_ql = 0
            actions.append(action_ql)

            if not env.ships[2]["done"]:
                sensores = env.get_genetic_sensors(obs_list[2], 2)
                action_gen = gen_cerebro.prever_acao(sensores)
            else:
                action_gen = 0
            actions.append(action_gen)

            results = env.step(actions)
            obs_list = [r[0] for r in results]

            for i, (_, _, _, info) in enumerate(results):
                if info.get("checkpoint_collected") and i == 0:
                    heuristic_ctrl.on_checkpoint_collected()

        env.render()

    env.close()


if __name__ == "__main__":
    main()
