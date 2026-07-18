"""
visualization.py — Funcoes de desenho para overlay do A*, linha guia e HUD do agente.
"""

import math
import pygame
import config as cfg
from agents.grid_map import CELL_SIZE


def simplify_path(path):
    if len(path) <= 2:
        return list(path)

    result = [path[0]]
    for i in range(1, len(path) - 1):
        prev = result[-1]
        curr = path[i]
        nxt = path[i + 1]

        v1 = (curr[0] - prev[0], curr[1] - prev[1])
        v2 = (nxt[0] - curr[0], nxt[1] - curr[1])

        m1 = math.hypot(*v1)
        m2 = math.hypot(*v2)

        if m1 > 0.001 and m2 > 0.001:
            dot = v1[0] * v2[0] + v1[1] * v2[1]
            cos_angle = dot / (m1 * m2)
            if cos_angle > 0.95:
                continue

        result.append(curr)

    result.append(path[-1])
    return result


def draw_a_star_overlay(screen, state):
    overlay = pygame.Surface(
        (cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), pygame.SRCALPHA
    )

    for cell in state.get("closed", []):
        r, c = cell
        rect = (c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(overlay, (0, 50, 150, 90), rect)
        pygame.draw.rect(overlay, (0, 80, 200, 90), rect, 1)

    for cell in state.get("open", []):
        r, c = cell
        rect = (c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(overlay, (0, 150, 255, 60), rect)
        pygame.draw.rect(overlay, (0, 200, 255, 60), rect, 1)

    curr = state.get("current")
    if curr:
        r, c = curr
        rect = (c * CELL_SIZE + 1, r * CELL_SIZE + 1, CELL_SIZE - 2, CELL_SIZE - 2)
        pygame.draw.rect(overlay, (255, 255, 0, 140), rect)
        pygame.draw.rect(overlay, (255, 255, 0, 200), rect, 2)

    screen.blit(overlay, (0, 0))


def draw_path_line(screen, path):
    if not path or len(path) < 2:
        return
    points = [(int(x), int(y)) for x, y in path]
    pygame.draw.lines(screen, (0, 255, 100), False, points, 3)


def draw_agent_hud(screen, attempt, margin, crash_info, crash_timer):
    if crash_timer <= 0:
        return

    from orbital_env import PixelFont

    alpha = min(255, crash_timer * 4)
    color = (255, 200, 60, alpha)

    text = f"ATTEMPT {attempt}  SAFETY +{margin:.0f}px"
    surf = PixelFont.render(text, (255, 200, 60))
    surf.set_alpha(alpha)

    x = (cfg.SCREEN_WIDTH - surf.get_width()) // 2
    y = cfg.SCREEN_HEIGHT - 30
    screen.blit(surf, (x, y))


def get_current_goal(env, ship_pos=None):
    uncollected = [cp for cp in env.checkpoints if not cp["collected"]]
    if not uncollected:
        return (float(env.station_pos[0]), float(env.station_pos[1]))
    if ship_pos is not None:
        sx, sy = ship_pos
        nearest = min(uncollected, key=lambda cp: math.hypot(
            sx - float(cp["pos"][0]), sy - float(cp["pos"][1])))
        return (float(nearest["pos"][0]), float(nearest["pos"][1]))
    return (float(uncollected[0]["pos"][0]), float(uncollected[0]["pos"][1]))
