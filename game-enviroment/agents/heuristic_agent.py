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
    draw_web_lines,
    draw_grid_overlay,
    draw_blocked_exclamations,
    draw_current_node_ripple,
    draw_start_beacon,
    draw_path_line,
    draw_agent_hud,
    get_current_goal,
)
from agents.replay_buffer import save_run, load_run, list_runs

NODES_PER_FRAME = 1
REPLAN_INTERVAL_MS = 1000
PATH_HOLD_FRAMES = 90
PLANNING_FRAME_DELAY = 200


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
    current_segment_raw = None

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

    planning_background = None
    start_cell = grid_map.pos_to_cell(*ship_pos)
    path_hold_counter = 0

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
                    current_segment_raw = None

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
                    planning_background = None
                    start_cell = grid_map.pos_to_cell(*ship_pos)
                    path_hold_counter = 0

        if phase == "planning":
            if planning_background is None:
                env.render()
                planning_background = env.screen.copy()
            else:
                env.screen.blit(planning_background, (0, 0))

            search_state = None

            if path_hold_counter > 0:
                path_hold_counter -= 1
                if path_hold_counter == 0:
                    phase = "flying"
                    last_replan_time = pygame.time.get_ticks()
                    last_dist_to_goal = math.hypot(
                        obs[0] - goal_pos[0], obs[1] - goal_pos[1]
                    )
            else:
                for _ in range(NODES_PER_FRAME):
                    try:
                        search_state = next(a_star_gen)
                    except StopIteration:
                        break
                    if search_state.get("path") is not None:
                        break

            if search_state is not None:
                draw_grid_overlay(env.screen)
                draw_a_star_overlay(env.screen, search_state)
                draw_web_lines(env.screen, search_state.get("came_from", {}))
                draw_current_node_ripple(
                    env.screen, search_state.get("current")
                )
                draw_start_beacon(env.screen, start_cell)
                draw_blocked_exclamations(
                    env.screen,
                    search_state.get("blocked", []),
                    env.planets,
                )

                found_path = search_state.get("path")
                if found_path is not None:
                    a_star_gen = None

                    if found_path:
                        current_segment_raw = list(found_path)
                        path = simplify_path(found_path)
                        autopilot = AutoPilot(path, env.planets)
                    else:
                        current_segment_raw = [ship_pos, goal_pos]
                        path = [ship_pos, goal_pos]
                        autopilot = AutoPilot(path, env.planets)

                    current_segment_path = path

                    draw_path_line(env.screen, path)
                    path_hold_counter = PATH_HOLD_FRAMES
                else:
                    pygame.time.wait(PLANNING_FRAME_DELAY)

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
                                "waypoints": current_segment_raw
                                if current_segment_raw
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
                            "waypoints": current_segment_raw
                            if current_segment_raw
                            else [],
                        })
                        checkpoint_order.append(current_segment_target)

                    grid_map = GridMap(env.planets, env.checkpoints,
                                       env.station_pos, global_margin)
                    ship_pos = (float(obs[0]), float(obs[1]))
                    goal_pos = get_current_goal(env, ship_pos)
                    current_segment_target = goal_pos
                    current_segment_path = None
                    current_segment_raw = None

                    planner = AStarPlanner(grid_map)
                    a_star_gen = planner.search(ship_pos, goal_pos)
                    path = None
                    autopilot = None
                    phase = "planning"
                    last_replan_time = pygame.time.get_ticks()
                    last_dist_to_goal = None
                    planning_background = None
                    start_cell = grid_map.pos_to_cell(*ship_pos)
                    path_hold_counter = 0
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
                                "waypoints": current_segment_raw
                                if current_segment_raw
                                else [],
                            })

                        grid_map = GridMap(env.planets, env.checkpoints,
                                           env.station_pos, global_margin)
                        ship_pos = (float(obs[0]), float(obs[1]))
                        goal_pos = get_current_goal(env, ship_pos)
                        current_segment_target = goal_pos
                        current_segment_path = None
                        current_segment_raw = None

                        planner = AStarPlanner(grid_map)
                        a_star_gen = planner.search(ship_pos, goal_pos)
                        path = None
                        autopilot = None
                        phase = "planning"
                        last_replan_time = now
                        last_dist_to_goal = None
                        planning_background = None
                        start_cell = grid_map.pos_to_cell(*ship_pos)
                        path_hold_counter = 0
                        continue
                    last_dist_to_goal = current_dist
                    last_replan_time = now

    env.close()
    pygame.quit()
    sys.exit()


# ============================================================
# Modo Treinado — carrega waypoints salvos, com replanning fallback
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
    checkpoint_order = run_data.get("checkpoint_order", [])

    print(f"Run {run_data['run_id']:03d} carregado:")
    print(f"  Segmentos: {len(segments)}")
    print(f"  Steps: {stats['steps']}  Thrusts: {stats['thrusts']}")
    print(f"  Reward: {stats['reward']:.0f}")

    global_margin = 0.0
    path = None
    autopilot = None
    seg_idx = 0
    collected_count = 0
    crash_timer = 0
    crash_info = ""

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
                    crash_info = (
                        f"TENTATIVA  MARGEM +{global_margin:.0f}px"
                    )
                    crash_timer = 120
                    obs = env.reset()
                    autopilot = None
                    path = None
                    seg_idx = 0
                    collected_count = 0
                    last_replan_time = pygame.time.get_ticks()
                    last_dist_to_goal = None

        if env.done:
            env.render()
            if path:
                draw_path_line(env.screen, path)
            if crash_timer > 0:
                draw_agent_hud(env.screen, 0, global_margin,
                               crash_info, crash_timer)
                crash_timer -= 1
            pygame.display.flip()
            continue

        if autopilot is None:
            if seg_idx < len(segments):
                seg = segments[seg_idx]
                path = [list(wp) for wp in seg["waypoints"]]
                autopilot = AutoPilot(path, env.planets)
            else:
                env.render()
                pygame.display.flip()
                continue

        if not autopilot.has_path() and seg_idx < len(segments):
            seg_idx += 1
            if seg_idx < len(segments):
                seg = segments[seg_idx]
                path = [list(wp) for wp in seg["waypoints"]]
                autopilot = AutoPilot(path, env.planets)

        action = autopilot.get_action(obs) if autopilot else 0
        obs, reward, done, info = env.step(action)
        env.render()

        if path:
            draw_path_line(env.screen, path)
        if crash_timer > 0:
            draw_agent_hud(env.screen, 0, global_margin,
                           crash_info, crash_timer)
            crash_timer -= 1
        pygame.display.flip()

        if env.done:
            status = env.last_info.get("status", "")
            if status == "docked":
                crash_info = f"SUCESSO!  Run {run_data['run_id']:03d}"
                crash_timer = 300
            else:
                global_margin += 5.0
                crash_info = f"FALHA  MARGEM +{global_margin:.0f}px"
                crash_timer = 120
        else:
            if info.get("checkpoint_collected"):
                collected_count += 1
                seg_idx = min(collected_count, len(segments) - 1)
                autopilot = None
                last_dist_to_goal = None
                continue

            now = pygame.time.get_ticks()
            if now - last_replan_time > REPLAN_INTERVAL_MS:
                ship_pos = (float(obs[0]), float(obs[1]))
                goal_pos = get_current_goal(env, ship_pos)
                current_dist = math.hypot(
                    obs[0] - goal_pos[0],
                    obs[1] - goal_pos[1],
                )
                if (
                    last_dist_to_goal is not None
                    and current_dist > last_dist_to_goal + 10
                ):
                    grid_map = GridMap(
                        env.planets, env.checkpoints,
                        env.station_pos, global_margin,
                    )
                    planner = AStarPlanner(grid_map)
                    full_gen = list(planner.search(ship_pos, goal_pos))
                    last_state = full_gen[-1] if full_gen else None
                    if last_state and last_state.get("path"):
                        path = last_state["path"]
                        autopilot = AutoPilot(path, env.planets)
                    last_replan_time = now
                    last_dist_to_goal = None
                    continue
                last_dist_to_goal = current_dist
                last_replan_time = now

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
