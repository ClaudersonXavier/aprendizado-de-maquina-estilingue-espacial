"""
heuristic_agent.py — Agente de Busca Heuristica (A* Visual) para Odisseia Orbital.

Arquitetura modular:
  agents/grid_map.py      — grid 40x30 com margem proporcional a massa
  agents/astar_planner.py — A* geradora com custo gravitacional
  agents/auto_pilot.py    — piloto com velocidade-alvo e evasao
  agents/visualization.py — overlay A*, linha guia e HUD
  agents/replay_buffer.py — save/load de experiencias de sucesso

Modos:
  python heuristic_agent.py                  → normal (A* + AutoPilot, salva ao vencer)
  python heuristic_agent.py --trained 001    → carrega run_001, pula A*
  python heuristic_agent.py --trained latest → carrega o run mais recente
"""

import sys
import os
import math

import pygame

_script_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_script_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

import config as cfg
from orbital_env import OrbitalEnv

from agents.grid_map import GridMap
from agents.astar_planner import AStarPlanner
from agents.auto_pilot import AutoPilot
from agents.visualization import (
    simplify_path,
    draw_a_star_overlay,
    draw_path_line,
    draw_agent_hud,
    get_current_goal,
)
from agents.replay_buffer import save_run, load_run, list_runs

NODES_PER_FRAME = 10
REPLAN_INTERVAL_MS = 1000


# ============================================================
# Modo Normal — A* ao vivo + salvamento ao vencer
# ============================================================
def main():
    env = OrbitalEnv(render_mode="human")
    obs = env.reset()

    global_margin = 0.0
    attempt = 1
    crash_info = ""
    crash_timer = 0
    crash_handled = False

    total_thrusts = 0
    segments = []
    checkpoint_order = []
    current_segment_target = None
    current_segment_path = None

    grid_map = GridMap(env.planets, env.checkpoints, env.station_pos,
                       global_margin)
    ship_pos = (float(obs[0]), float(obs[1]))
    goal_pos = get_current_goal(env, ship_pos)
    current_segment_target = goal_pos

    planner = AStarPlanner(grid_map)
    a_star_gen = planner.search(ship_pos, goal_pos)
    autopilot = None
    path = None

    phase = "planning"
    last_replan_time = pygame.time.get_ticks()
    last_dist_to_goal = None

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    global_margin += 5.0
                    attempt += 1
                    crash_info = (
                        f"TENTATIVA {attempt}  MARGEM +{global_margin:.0f}px"
                    )
                    crash_timer = 120
                    crash_handled = False
                    total_thrusts = 0
                    segments = []
                    checkpoint_order = []
                    current_segment_path = None

                    obs = env.reset()
                    grid_map = GridMap(env.planets, env.checkpoints,
                                       env.station_pos, global_margin)
                    ship_pos = (float(obs[0]), float(obs[1]))
                    goal_pos = get_current_goal(env, ship_pos)
                    current_segment_target = goal_pos

                    planner = AStarPlanner(grid_map)
                    a_star_gen = planner.search(ship_pos, goal_pos)
                    autopilot = None
                    path = None
                    phase = "planning"
                    last_replan_time = pygame.time.get_ticks()
                    last_dist_to_goal = None

        if phase == "planning":
            env.render()
            search_state = None

            for _ in range(NODES_PER_FRAME):
                try:
                    search_state = next(a_star_gen)
                except StopIteration:
                    break
                if search_state.get("path") is not None:
                    break

            if search_state is not None:
                draw_a_star_overlay(env.screen, search_state)

                found_path = search_state.get("path")
                if found_path is not None:
                    a_star_gen = None

                    if found_path:
                        path = simplify_path(found_path)
                        autopilot = AutoPilot(path, env.planets)
                    else:
                        path = [ship_pos, goal_pos]
                        autopilot = AutoPilot(path, env.planets)

                    current_segment_path = path

                    phase = "flying"
                    last_replan_time = pygame.time.get_ticks()
                    last_dist_to_goal = math.hypot(
                        obs[0] - goal_pos[0], obs[1] - goal_pos[1]
                    )

            if crash_timer > 0:
                draw_agent_hud(env.screen, attempt, global_margin,
                               crash_info, crash_timer)
                crash_timer -= 1

            pygame.display.flip()

        elif phase == "flying":
            if not env.done:
                action = autopilot.get_action(obs) if autopilot else 0
                obs, reward, done, info = env.step(action)
                if action != 0:
                    total_thrusts += 1

            env.render()

            if path:
                draw_path_line(env.screen, path)

            if crash_timer > 0:
                draw_agent_hud(env.screen, attempt, global_margin,
                               crash_info, crash_timer)
                crash_timer -= 1

            pygame.display.flip()

            if env.done:
                if not crash_handled:
                    status = env.last_info.get("status", "")
                    if status == "docked":
                        if current_segment_target is not None:
                            segments.append({
                                "target": current_segment_target,
                                "waypoints": current_segment_path
                                if current_segment_path
                                else [],
                            })

                        stats = {
                            "steps": env.episode_steps,
                            "thrusts": total_thrusts,
                            "fuel_used": (
                                cfg.MAX_FUEL - float(obs[4])
                            ),
                            "reward": float(env.episode_reward),
                            "checkpoints": sum(
                                1 for cp in env.checkpoints
                                if cp["collected"]
                            ),
                        }
                        run_id, filepath = save_run(
                            segments, checkpoint_order, stats
                        )
                        crash_info = (
                            f"SUCESSO!  Salvo run_{run_id:03d}.json"
                        )
                        crash_timer = 300
                    else:
                        global_margin += 5.0
                        attempt += 1
                        crash_info = (
                            f"TENTATIVA {attempt}"
                            f"  MARGEM +{global_margin:.0f}px"
                        )
                        crash_timer = 120
                    crash_handled = True
            else:
                crash_handled = False

                if info.get("checkpoint_collected"):
                    if current_segment_target is not None:
                        segments.append({
                            "target": current_segment_target,
                            "waypoints": current_segment_path
                            if current_segment_path
                            else [],
                        })
                        checkpoint_order.append(current_segment_target)

                    grid_map = GridMap(env.planets, env.checkpoints,
                                       env.station_pos, global_margin)
                    ship_pos = (float(obs[0]), float(obs[1]))
                    goal_pos = get_current_goal(env, ship_pos)
                    current_segment_target = goal_pos
                    current_segment_path = None

                    planner = AStarPlanner(grid_map)
                    a_star_gen = planner.search(ship_pos, goal_pos)
                    path = None
                    autopilot = None
                    phase = "planning"
                    last_replan_time = pygame.time.get_ticks()
                    last_dist_to_goal = None
                    continue

                now = pygame.time.get_ticks()
                if (
                    now - last_replan_time > REPLAN_INTERVAL_MS
                    and current_segment_target is not None
                ):
                    current_dist = math.hypot(
                        obs[0] - current_segment_target[0],
                        obs[1] - current_segment_target[1],
                    )
                    if (
                        last_dist_to_goal is not None
                        and current_dist > last_dist_to_goal + 10
                    ):
                        if current_segment_target is not None:
                            segments.append({
                                "target": current_segment_target,
                                "waypoints": current_segment_path
                                if current_segment_path
                                else [],
                            })

                        grid_map = GridMap(env.planets, env.checkpoints,
                                           env.station_pos, global_margin)
                        ship_pos = (float(obs[0]), float(obs[1]))
                        goal_pos = get_current_goal(env, ship_pos)
                        current_segment_target = goal_pos
                        current_segment_path = None

                        planner = AStarPlanner(grid_map)
                        a_star_gen = planner.search(ship_pos, goal_pos)
                        path = None
                        autopilot = None
                        phase = "planning"
                        last_replan_time = now
                        last_dist_to_goal = None
                        continue
                    last_dist_to_goal = current_dist
                    last_replan_time = now

    env.close()
    pygame.quit()
    sys.exit()


# ============================================================
# Modo Treinado — carrega waypoints salvos, sem A*
# ============================================================
def main_trained(run_id):
    run_data = load_run(run_id)
    if run_data is None:
        print(f"Run '{run_id}' nao encontrado.")
        print("Runs disponiveis:")
        for r in list_runs():
            rid = r["id"]
            rts = r["timestamp"][:19] if r["timestamp"] else "?"
            print(f"  run_{rid:03d}  {rts}  reward={r['reward']:.0f}")
        sys.exit(1)

    env = OrbitalEnv(render_mode="human")
    obs = env.reset()

    segments = run_data["segments"]
    stats = run_data["stats"]

    print(f"Run {run_data['run_id']:03d} carregado:")
    print(f"  Segmentos: {len(segments)}")
    print(f"  Steps: {stats['steps']}  Thrusts: {stats['thrusts']}")
    print(f"  Reward: {stats['reward']:.0f}")

    path = None
    autopilot = None
    seg_idx = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    obs = env.reset()
                    autopilot = None
                    path = None
                    seg_idx = 0
                    if seg_idx < len(segments):
                        seg = segments[seg_idx]
                        path = seg["waypoints"]
                        autopilot = AutoPilot(path, env.planets)

        if env.done:
            env.render()
            if path:
                draw_path_line(env.screen, path)
            pygame.display.flip()
            continue

        if autopilot is None:
            if seg_idx < len(segments):
                seg = segments[seg_idx]
                path = seg["waypoints"]
                autopilot = AutoPilot(path, env.planets)
            else:
                env.render()
                pygame.display.flip()
                continue

        if not autopilot.has_path() and seg_idx < len(segments):
            seg_idx += 1
            if seg_idx < len(segments):
                seg = segments[seg_idx]
                path = seg["waypoints"]
                autopilot = AutoPilot(path, env.planets)

        action = autopilot.get_action(obs) if autopilot else 0
        obs, reward, done, info = env.step(action)
        env.render()

        if path:
            draw_path_line(env.screen, path)
        pygame.display.flip()

    env.close()
    pygame.quit()
    sys.exit()


# ============================================================
# Entrada
# ============================================================
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
