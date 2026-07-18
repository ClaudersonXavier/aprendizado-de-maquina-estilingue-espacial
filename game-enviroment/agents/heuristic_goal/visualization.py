"""
visualization.py — Funcoes de desenho para overlay do A*, linha guia e HUD do agente.
"""

import math
import pygame
import config as cfg
from .grid_map import CELL_SIZE

_HALF_CELL = CELL_SIZE / 2


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


# ============================================================
# Snapshot do jogo (fundo congelado durante planejamento)
# ============================================================
def capture_game_snapshot(env):
    snapshot = pygame.Surface(
        (cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), pygame.SRCALPHA
    )
    snapshot.fill(cfg.COLOR_SPACE)

    env.render()
    snapshot.blit(env.screen, (0, 0))

    return snapshot


# ============================================================
# Overlay: grid 20x20 visivel
# ============================================================
def draw_grid_overlay(screen):
    grid_surf = pygame.Surface(
        (cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), pygame.SRCALPHA
    )

    cols = cfg.SCREEN_WIDTH // CELL_SIZE
    rows = cfg.SCREEN_HEIGHT // CELL_SIZE

    for r in range(rows + 1):
        y = r * CELL_SIZE
        pygame.draw.line(grid_surf, (15, 120, 220, 100), (0, y),
                         (cfg.SCREEN_WIDTH, y), 1)

    for c in range(cols + 1):
        x = c * CELL_SIZE
        pygame.draw.line(grid_surf, (15, 120, 220, 100), (x, 0),
                         (x, cfg.SCREEN_HEIGHT), 1)

    screen.blit(grid_surf, (0, 0))


# ============================================================
# Overlay: celulas open / closed / current
# ============================================================
def draw_a_star_overlay(screen, state):
    overlay = pygame.Surface(
        (cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), pygame.SRCALPHA
    )

    for cell in state.get("closed", []):
        r, c = cell
        rect = (c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(overlay, (0, 60, 160, 70), rect)
        pygame.draw.rect(overlay, (0, 100, 220, 70), rect, 1)

    for cell in state.get("open", []):
        r, c = cell
        rect = (c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(overlay, (0, 160, 255, 90), rect)
        pygame.draw.rect(overlay, (0, 220, 255, 90), rect, 1)

    curr = state.get("current")
    if curr:
        r, c = curr
        rect = (c * CELL_SIZE + 1, r * CELL_SIZE + 1,
                CELL_SIZE - 2, CELL_SIZE - 2)
        pygame.draw.rect(overlay, (255, 255, 40, 160), rect)
        pygame.draw.rect(overlay, (255, 255, 0, 220), rect, 2)

    screen.blit(overlay, (0, 0))


# ============================================================
# Teia de aranha: linhas conectando pais e filhos
# ============================================================
def draw_web_lines(screen, came_from, current_node=None):
    if not came_from:
        return

    web_surf = pygame.Surface(
        (cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), pygame.SRCALPHA
    )

    for child, parent in came_from.items():
        cr, cc = child
        pr, pc = parent
        cx = cc * CELL_SIZE + _HALF_CELL
        cy = cr * CELL_SIZE + _HALF_CELL
        px = pc * CELL_SIZE + _HALF_CELL
        py = pr * CELL_SIZE + _HALF_CELL
        pygame.draw.line(web_surf, (0, 180, 255, 80), (px, py), (cx, cy), 2)

    screen.blit(web_surf, (0, 0))


# ============================================================
# Anel pulsante no no atual
# ============================================================
def draw_current_node_ripple(screen, current_node):
    if current_node is None:
        return

    now = pygame.time.get_ticks()

    r, c = current_node
    cx = int(c * CELL_SIZE + _HALF_CELL)
    cy = int(r * CELL_SIZE + _HALF_CELL)

    ripple_surf = pygame.Surface(
        (cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), pygame.SRCALPHA
    )

    for i in range(3):
        phase = (now * 0.005 + i * 2.0) % (math.pi * 2)
        radius = int(8 + math.sin(phase) * 5 + i * 8)
        alpha = max(0, int(100 - radius * 3))
        if alpha > 0 and radius > 0:
            pygame.draw.circle(ripple_surf, (255, 255, 100, alpha),
                               (cx, cy), radius, 1)

    screen.blit(ripple_surf, (0, 0))


# ============================================================
# Exclamacao vermelha nos planetas bloqueados
# ============================================================
def draw_blocked_exclamations(screen, blocked, planets):
    if not blocked or not planets:
        return

    from orbital_env import PixelFont

    planet_hits = {}
    for r, c in blocked:
        cx = c * CELL_SIZE + _HALF_CELL
        cy = r * CELL_SIZE + _HALF_CELL
        nearest = None
        nearest_dist = float("inf")
        for idx, p in enumerate(planets):
            px = float(p["pos"][0])
            py = float(p["pos"][1])
            dist = math.hypot(cx - px, cy - py)
            if dist < nearest_dist:
                nearest_dist = dist
                nearest = idx
        if nearest is not None:
            planet_hits[nearest] = max(planet_hits.get(nearest, 0),
                                       nearest_dist)

    now = pygame.time.get_ticks()
    pulse = (math.sin(now * 0.006) + 1) / 2
    alpha = int(180 + pulse * 75)

    excl = PixelFont.render("!", (255, 30, 30))
    excl_scaled = pygame.transform.scale(excl,
                                         (excl.get_width() * 3,
                                          excl.get_height() * 3))

    hit_surf = pygame.Surface(
        (cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), pygame.SRCALPHA
    )

    for p_idx in planet_hits:
        planet = planets[p_idx]
        px = int(planet["pos"][0])
        py = int(planet["pos"][1]) - int(planet["radius"]) - 20

        glow_radius = int(10 + pulse * 4)
        pygame.draw.circle(hit_surf, (255, 30, 30, alpha // 4),
                           (px, py + excl_scaled.get_height() // 2),
                           glow_radius)

        es = excl_scaled.copy()
        es.set_alpha(alpha)
        sx = px - es.get_width() // 2
        sy = py
        hit_surf.blit(es, (sx, sy))

    screen.blit(hit_surf, (0, 0))


# ============================================================
# Ponto de origem (onde a teia comecou)
# ============================================================
def draw_start_beacon(screen, start_cell):
    if start_cell is None:
        return
    r, c = start_cell
    cx = int(c * CELL_SIZE + _HALF_CELL)
    cy = int(r * CELL_SIZE + _HALF_CELL)

    now = pygame.time.get_ticks()
    pulse = (math.sin(now * 0.004) + 1) / 2

    beacon = pygame.Surface(
        (cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), pygame.SRCALPHA
    )
    radius = int(4 + pulse * 3)
    alpha = int(180 + pulse * 75)
    pygame.draw.circle(beacon, (255, 255, 100, alpha), (cx, cy), radius)
    pygame.draw.circle(beacon, (255, 255, 255, alpha), (cx, cy),
                       max(1, radius - 2))

    screen.blit(beacon, (0, 0))


# ============================================================
# Linha guia verde (waypoints)
# ============================================================
def draw_path_line(screen, path):
    if not path or len(path) < 2:
        return
    points = [(int(x), int(y)) for x, y in path]
    pygame.draw.lines(screen, (0, 255, 100), False, points, 3)


# ============================================================
# HUD do agente
# ============================================================
def draw_agent_hud(screen, attempt, margin, crash_info, crash_timer):
    if crash_timer <= 0:
        return

    from orbital_env import PixelFont

    alpha = min(255, crash_timer * 4)

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
