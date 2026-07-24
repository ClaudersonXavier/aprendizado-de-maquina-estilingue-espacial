"""
race_env.py — Ambiente de corrida com 3 naves independentes.
Cada nave tem seus proprios checkpoints coloridos e estado.
Fisica compartilhada (planetas, gravidade), sem colisao entre naves.
"""

import math
import random
import numpy as np
import pygame
import config as cfg
import physics as phys


SHIP_COLORS = [
    (0, 100, 255),     # Azul   — Heuristico (A*)
    (255, 60, 180),    # Rosa   — Q-Learning
    (255, 220, 0),     # Amarelo — Genetico
]

SHIP_NAMES = ["HEURISTICO", "Q-LEARNING", "GENETICO"]


class RaceEnv:

    def __init__(self, render_mode=None):
        self.render_mode = render_mode

        self.planets = [
            {
                "pos": np.array(p["pos"], dtype=np.float64),
                "radius": p["radius"],
                "mass": p["mass"],
                "color": p["color"],
            }
            for p in cfg.PLANETS
        ]

        self.station_pos = np.array(cfg.STATION_POS, dtype=np.float64)
        self.station_radius = cfg.STATION_RADIUS

        self.ships = []
        self._init_ships()

        self.screen = None
        self.canvas = None
        self.clock = None
        self.stars = []

        if render_mode is not None:
            self._init_pygame()

    def _init_ships(self):
        self.ships = []
        for i in range(3):
            checkpoints = []
            for cp in cfg.CHECKPOINTS:
                checkpoints.append({
                    "pos": np.array(cp["pos"], dtype=np.float64),
                    "radius": cp["radius"],
                    "collected": False,
                })
            self.ships.append({
                "pos": np.array(cfg.SHIP_START_POS, dtype=np.float64).copy(),
                "vel": np.zeros(2, dtype=np.float64),
                "fuel": cfg.MAX_FUEL,
                "done": False,
                "status": "alive",
                "trail": [tuple(np.array(cfg.SHIP_START_POS, dtype=np.float64))],
                "steps": 0,
                "checkpoints": checkpoints,
                "_escaped": False,
                "color": SHIP_COLORS[i],
                "name": SHIP_NAMES[i],
            })

    def reset(self):
        for ship in self.ships:
            ship["pos"] = np.array(cfg.SHIP_START_POS, dtype=np.float64).copy()
            ship["vel"] = np.zeros(2, dtype=np.float64)
            ship["fuel"] = cfg.MAX_FUEL
            ship["done"] = False
            ship["status"] = "alive"
            ship["trail"] = [tuple(np.array(cfg.SHIP_START_POS, dtype=np.float64))]
            ship["steps"] = 0
            ship["_escaped"] = False
            for cp in ship["checkpoints"]:
                cp["collected"] = False
        return [self.get_obs(i) for i in range(3)]

    def get_obs(self, idx):
        ship = self.ships[idx]
        checkpoint_dist = 0.0
        for cp in ship["checkpoints"]:
            if not cp["collected"]:
                checkpoint_dist = float(np.linalg.norm(ship["pos"] - cp["pos"]))
                break
        station_dist = float(np.linalg.norm(ship["pos"] - self.station_pos))
        return np.array([
            float(ship["pos"][0]), float(ship["pos"][1]),
            float(ship["vel"][0]), float(ship["vel"][1]),
            float(ship["fuel"]), checkpoint_dist, station_dist,
        ], dtype=np.float64)

    def step(self, actions):
        results = []
        for i, ship in enumerate(self.ships):
            if ship["done"]:
                obs = self.get_obs(i)
                results.append((obs, 0.0, True, {
                    "status": ship["status"],
                    "checkpoint_collected": False,
                }))
                continue

            action = actions[i]
            reward = 0.0
            info = {"status": "alive", "checkpoint_collected": False}

            thrust_available = False
            if action != 0 and ship["fuel"] >= cfg.FUEL_COST_PER_THRUST:
                ship["fuel"] -= cfg.FUEL_COST_PER_THRUST
                thrust_available = True
                reward += cfg.REWARD_THRUST_COST

            if ship["_escaped"]:
                active_planets = self.planets
            else:
                active_planets = [
                    p for j, p in enumerate(self.planets)
                    if j != cfg.LAUNCH_PLANET_INDEX
                ]
            grav_accel = phys.total_gravity(ship["pos"], active_planets, cfg.G)

            if thrust_available:
                thrust_accel = phys.thrust_vector(action, cfg.THRUST_POWER)
            else:
                thrust_accel = np.zeros(2, dtype=np.float64)

            total_accel = grav_accel + thrust_accel
            ship["pos"], ship["vel"] = phys.apply_kinematics(
                ship["pos"], ship["vel"], total_accel, cfg.MAX_SPEED
            )

            ship["trail"].append(tuple(ship["pos"]))
            if len(ship["trail"]) > cfg.MAX_TRAIL_LENGTH:
                ship["trail"].pop(0)

            if not ship["_escaped"]:
                launch_planet = self.planets[cfg.LAUNCH_PLANET_INDEX]
                dist_to_launch = float(
                    np.linalg.norm(ship["pos"] - launch_planet["pos"])
                )
                if dist_to_launch > cfg.LAUNCH_ESCAPE_DISTANCE:
                    ship["_escaped"] = True

            crashed = False
            for planet in self.planets:
                if phys.check_circle_collision(
                    ship["pos"], cfg.SHIP_RADIUS,
                    planet["pos"], planet["radius"],
                ):
                    ship["done"] = True
                    ship["status"] = "crashed_planet"
                    crashed = True
                    break

            if crashed:
                results.append((self.get_obs(i), cfg.REWARD_FAILURE_COLLISION, True, info))
                continue

            if phys.is_out_of_bounds(
                ship["pos"], cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT
            ):
                ship["done"] = True
                ship["status"] = "out_of_bounds"
                results.append((self.get_obs(i), cfg.REWARD_FAILURE_OOB, True, info))
                continue

            for cp in ship["checkpoints"]:
                if cp["collected"]:
                    continue
                if phys.check_circle_collision(
                    ship["pos"], cfg.SHIP_RADIUS,
                    cp["pos"], cp["radius"],
                ):
                    cp["collected"] = True
                    ship["fuel"] = min(ship["fuel"] + cfg.FUEL_PICKUP, cfg.MAX_FUEL)
                    reward += cfg.REWARD_CHECKPOINT
                    info["checkpoint_collected"] = True

            all_cp = all(cp["collected"] for cp in ship["checkpoints"])
            if all_cp:
                station_center = (
                    float(self.station_pos[0]),
                    float(self.station_pos[1]),
                )
                if phys.check_circle_rect_collision(
                    ship["pos"], cfg.SHIP_RADIUS,
                    station_center, cfg.STATION_WIDTH, cfg.STATION_HEIGHT,
                ):
                    reward += cfg.REWARD_SUCCESS + ship["fuel"] * cfg.REWARD_FUEL_BONUS_FACTOR
                    ship["done"] = True
                    ship["status"] = "docked"
                    info["status"] = "docked"
                    results.append((self.get_obs(i), reward, True, info))
                    continue

            if ship["fuel"] <= 0.0:
                ship["done"] = True
                ship["status"] = "no_fuel"
                info["status"] = "no_fuel"
                results.append((self.get_obs(i), cfg.REWARD_FAILURE_NO_FUEL, True, info))
                continue

            reward += cfg.REWARD_STEP
            ship["steps"] += 1
            results.append((self.get_obs(i), reward, ship["done"], info))

        return results

    def get_genetic_sensors(self, obs, ship_idx):
        ship = self.ships[ship_idx]
        pos = ship["pos"]
        vel = ship["vel"]
        fuel = ship["fuel"]

        best_dist = float("inf")
        target_pos = self.station_pos
        for cp in ship["checkpoints"]:
            if not cp["collected"]:
                d = float(np.linalg.norm(cp["pos"] - pos))
                if d < best_dist:
                    best_dist = d
                    target_pos = cp["pos"]

        dx = float(target_pos[0] - pos[0])
        dy = float(target_pos[1] - pos[1])
        vx = float(vel[0])
        vy = float(vel[1])

        launch_planet = self.planets[cfg.LAUNCH_PLANET_INDEX]
        dist_to_launch = float(np.linalg.norm(pos - launch_planet["pos"]))
        escaped = dist_to_launch > cfg.LAUNCH_ESCAPE_DISTANCE

        perigos = []
        for j, planet in enumerate(self.planets):
            if not escaped and j == cfg.LAUNCH_PLANET_INDEX:
                continue
            dist = float(np.linalg.norm(pos - planet["pos"]))
            surface_dist = dist - planet["radius"]
            p_dx = float(planet["pos"][0] - pos[0])
            p_dy = float(planet["pos"][1] - pos[1])
            perigos.append((surface_dist, p_dx, p_dy))

        perigos.sort(key=lambda x: x[0])
        p1 = perigos[0] if perigos else (999.0, 0.0, 0.0)
        p2 = perigos[1] if len(perigos) > 1 else (999.0, 0.0, 0.0)

        dist_alvo = max(math.hypot(dx, dy), 1.0)
        vel_toward = (vx * dx + vy * dy) / dist_alvo / 2.75

        return [dx, dy, vx, vy, fuel, p1[0], p1[1], p1[2], p2[0], p2[1], p2[2], vel_toward]

    # ============================================================
    # Renderizacao
    # ============================================================

    def render(self):
        if self.canvas is None:
            self._init_pygame()

        self.canvas.fill(cfg.COLOR_SPACE)

        self._draw_grid()
        self._draw_starfield()
        self._draw_trails()
        self._draw_planets()
        self._draw_checkpoints()
        self._draw_station()
        self._draw_ships()
        self._draw_hud()

        all_done = all(s["done"] for s in self.ships)
        if all_done:
            self._draw_leaderboard()

        scaled = pygame.transform.scale(
            self.canvas, (cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT)
        )
        self.screen.blit(scaled, (0, 0))
        pygame.display.flip()
        self.clock.tick(cfg.FPS)

    def close(self):
        if self.screen is not None:
            pygame.quit()
            self.screen = None
            self.canvas = None
            self.clock = None

    # ============================================================
    # Pygame Init
    # ============================================================

    def _init_pygame(self):
        if self.screen is not None:
            return
        pygame.init()
        self.screen = pygame.display.set_mode(
            (cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT)
        )
        pygame.display.set_caption("Odisseia Orbital — Corrida dos Agentes")
        self.canvas = pygame.Surface(
            (cfg.RENDER_WIDTH, cfg.RENDER_HEIGHT)
        )
        self.clock = pygame.time.Clock()
        self._generate_stars()

    def _generate_stars(self):
        self.stars = []
        for _ in range(cfg.STAR_COUNT):
            self.stars.append({
                "x": random.randint(0, cfg.RENDER_WIDTH - 1),
                "y": random.randint(0, cfg.RENDER_HEIGHT - 1),
                "color": random.choice([
                    cfg.COLOR_GRAY, cfg.COLOR_WHITE, cfg.COLOR_YELLOW,
                    cfg.COLOR_CYAN,
                ]),
                "phase": random.randint(0, 120),
                "period": random.randint(40, 100),
            })

    def _draw_grid(self):
        for x in range(0, cfg.RENDER_WIDTH, cfg.GRID_SPACING):
            for y in range(0, cfg.RENDER_HEIGHT, cfg.GRID_DOT_GAP):
                if (y // cfg.GRID_DOT_GAP) % 2 == 0:
                    if 0 <= x < cfg.RENDER_WIDTH and y < cfg.RENDER_HEIGHT:
                        self.canvas.set_at((x, y), cfg.COLOR_DARK_GRAY)
        for y in range(0, cfg.RENDER_HEIGHT, cfg.GRID_SPACING):
            for x in range(0, cfg.RENDER_WIDTH, cfg.GRID_DOT_GAP):
                if (x // cfg.GRID_DOT_GAP) % 2 == 0:
                    if x < cfg.RENDER_WIDTH and 0 <= y < cfg.RENDER_HEIGHT:
                        self.canvas.set_at((x, y), cfg.COLOR_DARK_GRAY)

    def _draw_starfield(self):
        current_time = pygame.time.get_ticks()
        for star in self.stars:
            frame = (current_time // 16) % star["period"]
            visible = frame < star["period"] * 0.7 or (
                frame >= star["period"] * 0.85 and star["phase"] % 3 == 0
            )
            if visible:
                sx, sy = star["x"], star["y"]
                if 0 <= sx < cfg.RENDER_WIDTH and 0 <= sy < cfg.RENDER_HEIGHT:
                    self.canvas.set_at((sx, sy), star["color"])

    def _draw_trails(self):
        scale = cfg.RENDER_WIDTH / cfg.SCREEN_WIDTH
        for ship in self.ships:
            if len(ship["trail"]) < 2:
                continue
            r, g, b = ship["color"]
            trail_color = (r // 2, g // 2, b // 2)
            for idx in range(0, len(ship["trail"]) - 1, 3):
                p = ship["trail"][idx]
                rx = int(p[0] * scale)
                ry = int(p[1] * scale)
                if 2 <= rx < cfg.RENDER_WIDTH - 2 and 2 <= ry < cfg.RENDER_HEIGHT - 2:
                    pygame.draw.rect(self.canvas, trail_color, (rx - 1, ry - 1, 3, 3))

    def _draw_planets(self):
        scale = cfg.RENDER_WIDTH / cfg.SCREEN_WIDTH
        for i, planet in enumerate(self.planets):
            px = int(planet["pos"][0] * scale)
            py = int(planet["pos"][1] * scale)
            radius = int(planet["radius"] * scale)
            color = planet["color"]

            if i == 1:
                self._draw_giant(px, py, radius, color)
                continue

            pygame.draw.circle(self.canvas, color, (px, py), radius)
            pygame.draw.circle(self.canvas, cfg.COLOR_BLACK, (px, py), radius, 2)

            if i == 0:
                plat_x = px + radius - 6
                plat_y = py - 8
                pygame.draw.rect(self.canvas, cfg.COLOR_GRAY,
                                 (plat_x, plat_y, 6, 8))
                pygame.draw.rect(self.canvas, cfg.COLOR_WHITE,
                                 (plat_x, plat_y, 6, 8), 1)
                pygame.draw.rect(self.canvas, cfg.COLOR_CYAN,
                                 (plat_x + 2, plat_y + 2, 2, 2))

    def _draw_giant(self, px, py, radius, color):
        for y in range(py - radius, py + radius + 1):
            dx = int(math.sqrt(max(0, radius * radius - (y - py) * (y - py))))
            if dx > 0:
                for x in range(px - dx, px + dx + 1):
                    if (x + y) % 5 == 0:
                        c = tuple(min(255, v + 30) for v in color)
                        self.canvas.set_at((x, y), c)

        ring_r = radius + 5
        pygame.draw.circle(self.canvas, cfg.COLOR_CYAN, (px, py), ring_r, 2)
        pygame.draw.circle(self.canvas, cfg.COLOR_MAGENTA, (px, py), ring_r + 5, 1)

        storm_x = px + radius // 3
        storm_y = py - radius // 3
        storm_w = max(4, radius // 3)
        storm_h = max(2, radius // 5)
        pygame.draw.ellipse(self.canvas, cfg.COLOR_ORANGE,
                            (storm_x - storm_w, storm_y - storm_h,
                             storm_w * 2, storm_h * 2), 1)

        pygame.draw.circle(self.canvas, color, (px, py), radius)
        pygame.draw.circle(self.canvas, cfg.COLOR_BLACK, (px, py), radius, 2)

    def _draw_checkpoints(self):
        scale = cfg.RENDER_WIDTH / cfg.SCREEN_WIDTH

        for cp_idx, cp_pos in enumerate(cfg.CHECKPOINTS):
            cx = int(cp_pos["pos"][0] * scale)
            cy = int(cp_pos["pos"][1] * scale)
            s = int(cp_pos["radius"] * scale)

            layers = [
                (2, s + 1),          # amarelo (genetico) — externo
                (1, s - 1),          # rosa (q-learning) — meio
                (0, max(3, s - 3)),  # azul (heuristico) — centro
            ]

            for ship_idx, size in layers:
                ship = self.ships[ship_idx]
                if ship["checkpoints"][cp_idx]["collected"]:
                    continue

                diamond = [
                    (cx, cy - size),
                    (cx + size, cy),
                    (cx, cy + size),
                    (cx - size, cy),
                ]
                pygame.draw.polygon(self.canvas, ship["color"], diamond)
                pygame.draw.polygon(self.canvas, cfg.COLOR_BLACK, diamond, 1)

    def _draw_station(self):
        scale = cfg.RENDER_WIDTH / cfg.SCREEN_WIDTH
        sx = int(self.station_pos[0] * scale)
        sy = int(self.station_pos[1] * scale)
        hw = int(cfg.STATION_WIDTH * scale) // 2
        hh = int(cfg.STATION_HEIGHT * scale) // 2
        current_time = pygame.time.get_ticks()

        all_docked = all(s["status"] == "docked" and s["done"] for s in self.ships)
        any_done = all(s["done"] for s in self.ships)

        body_rect = pygame.Rect(sx - hw, sy - hh, hw * 2, hh * 2)
        pygame.draw.rect(self.canvas, cfg.COLOR_GRAY, body_rect)
        pygame.draw.rect(self.canvas, cfg.COLOR_BLACK, body_rect, 2)
        pygame.draw.rect(self.canvas, cfg.COLOR_CYAN, body_rect, 1)

        panel_w = 5
        panel_h = 10
        for side in [-1, 1]:
            panel_x = sx + side * (hw + panel_w + 3)
            panel_y = sy - panel_h // 2
            panel_rect = pygame.Rect(panel_x - panel_w // 2, panel_y, panel_w, panel_h)
            pygame.draw.rect(self.canvas, cfg.COLOR_DARK_GRAY, panel_rect)
            pygame.draw.rect(self.canvas, cfg.COLOR_CYAN, panel_rect, 1)
            for gy in range(panel_y + 2, panel_y + panel_h - 1, 2):
                pygame.draw.line(self.canvas, cfg.COLOR_GRAY,
                                 (panel_x - panel_w // 2 + 1, gy),
                                 (panel_x + panel_w // 2 - 1, gy), 1)

        if any_done:
            dock_on = (current_time // 300) % 2
            dock_color = cfg.COLOR_GREEN if dock_on else cfg.COLOR_DARK_GRAY
        else:
            dock_color = cfg.COLOR_DARK_GRAY
        pygame.draw.rect(self.canvas, dock_color, (sx - 2, sy - 2, 5, 5))
        pygame.draw.rect(self.canvas, cfg.COLOR_BLACK, (sx - 3, sy - 3, 7, 7), 1)

    def _draw_ships(self):
        scale = cfg.RENDER_WIDTH / cfg.SCREEN_WIDTH
        for ship in self.ships:
            x = ship["pos"][0] * scale
            y = ship["pos"][1] * scale
            vx, vy = float(ship["vel"][0]), float(ship["vel"][1])

            speed = math.hypot(vx, vy)
            if speed > 0.05:
                angle = math.atan2(vy, vx)
            else:
                angle = 0.0

            size = 7
            color = ship["color"]

            nose = (
                x + size * math.cos(angle),
                y + size * math.sin(angle),
            )
            left = (
                x + size * 0.5 * math.cos(angle + 2.6),
                y + size * 0.5 * math.sin(angle + 2.6),
            )
            right = (
                x + size * 0.5 * math.cos(angle - 2.6),
                y + size * 0.5 * math.sin(angle - 2.6),
            )
            rear = (
                x + size * 0.25 * math.cos(angle + math.pi),
                y + size * 0.25 * math.sin(angle + math.pi),
            )

            pts = [
                (int(nose[0]), int(nose[1])),
                (int(left[0]), int(left[1])),
                (int(rear[0]), int(rear[1])),
                (int(right[0]), int(right[1])),
            ]

            if ship["done"]:
                ghost = tuple(c // 2 for c in color)
                pygame.draw.polygon(self.canvas, ghost, pts)
                pygame.draw.polygon(self.canvas, cfg.COLOR_DARK_GRAY, pts, 1)
            else:
                pygame.draw.polygon(self.canvas, color, pts)
                pygame.draw.polygon(self.canvas, cfg.COLOR_BLACK, pts, 1)
                brighter = tuple(min(255, c + 80) for c in color)
                pygame.draw.polygon(self.canvas, brighter, pts, 1)

            cockpit_x = int(x + size * 0.3 * math.cos(angle))
            cockpit_y = int(y + size * 0.3 * math.sin(angle))
            pygame.draw.rect(self.canvas, cfg.COLOR_CYAN,
                             (cockpit_x - 1, cockpit_y - 1, 3, 3))

    def _draw_hud(self):
        x, y = 4, 4
        for i, ship in enumerate(self.ships):
            text = f"{ship['name'][:4]} {ship['steps']:4d}"
            self._blit_text(text, x, y, ship["color"])
            y += 9

    def _draw_leaderboard(self):
        overlay = pygame.Surface((cfg.RENDER_WIDTH, cfg.RENDER_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.canvas.blit(overlay, (0, 0))

        frame_w, frame_h = 280, 160
        frame_x = (cfg.RENDER_WIDTH - frame_w) // 2
        frame_y = (cfg.RENDER_HEIGHT - frame_h) // 2

        pygame.draw.rect(self.canvas, cfg.COLOR_BLACK,
                         (frame_x, frame_y, frame_w, frame_h))
        pygame.draw.rect(self.canvas, cfg.COLOR_CYAN,
                         (frame_x, frame_y, frame_w, frame_h), 2)

        title = "CORRIDA FINALIZADA!"
        tw = len(title) * 6
        self._blit_text(title, frame_x + (frame_w - tw) // 2, frame_y + 10, cfg.COLOR_CYAN)

        ranked = sorted(self.ships, key=lambda s: (
            0 if s["status"] == "docked" else 1,
            s["steps"]
        ))

        medals = ["1.", "2.", "3."]
        for i, ship in enumerate(ranked):
            line_y = frame_y + 32 + i * 24
            status = ship["status"].upper()
            if status == "DOCKED":
                steps_str = f"{ship['steps']} steps"
            elif status == "CRASHED_PLANET":
                steps_str = "COLIDIU"
            elif status == "OUT_OF_BOUNDS":
                steps_str = "FORA"
            elif status == "NO_FUEL":
                steps_str = "SEM COMB."
            else:
                steps_str = f"{ship['steps']} steps"

            line = f"{medals[i]} {ship['name']:12s} {steps_str}"
            self._blit_text(line, frame_x + 16, line_y, ship["color"])

        hint_y = frame_y + frame_h - 20
        hint = "[R] RECOMECAR  [ESC] SAIR"
        hw = len(hint) * 6
        self._blit_text(hint, frame_x + (frame_w - hw) // 2, hint_y, cfg.COLOR_WHITE)

    def _blit_text(self, text, x, y, color):
        rendered = PixelFont.render(text, color)
        self.canvas.blit(rendered, (x, y))
        return rendered.get_width()


class PixelFont:
    CHAR_W = 5
    CHAR_H = 7

    _GLYPHS = {}

    @classmethod
    def _init_glyphs(cls):
        if cls._GLYPHS:
            return

        def glyph(rows):
            g = [[False] * cls.CHAR_W for _ in range(cls.CHAR_H)]
            for y, row in enumerate(rows[:cls.CHAR_H]):
                for x, ch in enumerate(row[:cls.CHAR_W]):
                    g[y][x] = (ch == '#')
            return g

        cls._GLYPHS['A'] = glyph(['.###.', '#...#', '#...#', '#####', '#...#', '#...#', '#...#'])
        cls._GLYPHS['B'] = glyph(['####.', '#...#', '####.', '#...#', '#...#', '#...#', '####.'])
        cls._GLYPHS['C'] = glyph(['.###.', '#...#', '#....', '#....', '#....', '#...#', '.###.'])
        cls._GLYPHS['D'] = glyph(['####.', '#...#', '#...#', '#...#', '#...#', '#...#', '####.'])
        cls._GLYPHS['E'] = glyph(['#####', '#....', '####.', '#....', '#....', '#....', '#####'])
        cls._GLYPHS['F'] = glyph(['#####', '#....', '####.', '#....', '#....', '#....', '#....'])
        cls._GLYPHS['G'] = glyph(['.###.', '#...#', '#....', '#.###', '#...#', '#...#', '.###.'])
        cls._GLYPHS['H'] = glyph(['#...#', '#...#', '#####', '#...#', '#...#', '#...#', '#...#'])
        cls._GLYPHS['I'] = glyph(['#####', '..#..', '..#..', '..#..', '..#..', '..#..', '#####'])
        cls._GLYPHS['J'] = glyph(['#####', '...#.', '...#.', '...#.', '...#.', '#..#.', '.##..'])
        cls._GLYPHS['K'] = glyph(['#...#', '#..#.', '###..', '##...', '###..', '#..#.', '#...#'])
        cls._GLYPHS['L'] = glyph(['#....', '#....', '#....', '#....', '#....', '#....', '#####'])
        cls._GLYPHS['M'] = glyph(['#...#', '##.##', '#.#.#', '#.#.#', '#...#', '#...#', '#...#'])
        cls._GLYPHS['N'] = glyph(['#...#', '##..#', '#.#.#', '#..##', '#...#', '#...#', '#...#'])
        cls._GLYPHS['O'] = glyph(['.###.', '#...#', '#...#', '#...#', '#...#', '#...#', '.###.'])
        cls._GLYPHS['P'] = glyph(['####.', '#...#', '#...#', '####.', '#....', '#....', '#....'])
        cls._GLYPHS['Q'] = glyph(['.###.', '#...#', '#...#', '#...#', '#.#.#', '#..#.', '.##.#'])
        cls._GLYPHS['R'] = glyph(['####.', '#...#', '#...#', '####.', '###..', '#..#.', '#...#'])
        cls._GLYPHS['S'] = glyph(['.###.', '#...#', '#....', '.###.', '....#', '#...#', '.###.'])
        cls._GLYPHS['T'] = glyph(['#####', '..#..', '..#..', '..#..', '..#..', '..#..', '..#..'])
        cls._GLYPHS['U'] = glyph(['#...#', '#...#', '#...#', '#...#', '#...#', '#...#', '.###.'])
        cls._GLYPHS['V'] = glyph(['#...#', '#...#', '#...#', '#...#', '.#.#.', '.#.#.', '..#..'])
        cls._GLYPHS['W'] = glyph(['#...#', '#...#', '#...#', '#.#.#', '#.#.#', '##.##', '#...#'])
        cls._GLYPHS['X'] = glyph(['#...#', '.#.#.', '..#..', '..#..', '..#..', '.#.#.', '#...#'])
        cls._GLYPHS['Y'] = glyph(['#...#', '.#.#.', '..#..', '..#..', '..#..', '..#..', '..#..'])
        cls._GLYPHS['Z'] = glyph(['#####', '....#', '...#.', '..#..', '.#...', '#....', '#####'])
        cls._GLYPHS['0'] = glyph(['.###.', '#...#', '#..##', '#.#.#', '##..#', '#...#', '.###.'])
        cls._GLYPHS['1'] = glyph(['..#..', '.##..', '..#..', '..#..', '..#..', '..#..', '#####'])
        cls._GLYPHS['2'] = glyph(['.###.', '#...#', '....#', '...#.', '..#..', '.#...', '#####'])
        cls._GLYPHS['3'] = glyph(['.###.', '#...#', '....#', '..##.', '....#', '#...#', '.###.'])
        cls._GLYPHS['4'] = glyph(['...#.', '..##.', '.#.#.', '#..#.', '#####', '...#.', '...#.'])
        cls._GLYPHS['5'] = glyph(['#####', '#....', '####.', '....#', '....#', '#...#', '.###.'])
        cls._GLYPHS['6'] = glyph(['.###.', '#...#', '#....', '####.', '#...#', '#...#', '.###.'])
        cls._GLYPHS['7'] = glyph(['#####', '....#', '...#.', '..#..', '.#...', '#....', '#....'])
        cls._GLYPHS['8'] = glyph(['.###.', '#...#', '#...#', '.###.', '#...#', '#...#', '.###.'])
        cls._GLYPHS['9'] = glyph(['.###.', '#...#', '#...#', '.####', '....#', '#...#', '.###.'])
        cls._GLYPHS['.'] = glyph(['.....', '.....', '.....', '.....', '.....', '.....', '..#..'])
        cls._GLYPHS['!'] = glyph(['..#..', '..#..', '..#..', '..#..', '..#..', '.....', '..#..'])
        cls._GLYPHS[':'] = glyph(['.....', '..#..', '.....', '.....', '..#..', '.....', '.....'])
        cls._GLYPHS['-'] = glyph(['.....', '.....', '#####', '.....', '.....', '.....', '.....'])
        cls._GLYPHS[' '] = glyph(['.....', '.....', '.....', '.....', '.....', '.....', '.....'])
        cls._GLYPHS['/'] = glyph(['....#', '...#.', '...#.', '..#..', '.#...', '.#...', '#....'])
        cls._GLYPHS['['] = glyph(['###..', '#....', '#....', '#....', '#....', '#....', '###..'])
        cls._GLYPHS[']'] = glyph(['..###', '....#', '....#', '....#', '....#', '....#', '..###'])
        cls._GLYPHS['('] = glyph(['...#.', '..#..', '.#...', '.#...', '.#...', '..#..', '...#.'])
        cls._GLYPHS[')'] = glyph(['.#...', '..#..', '...#.', '...#.', '...#.', '..#..', '.#...'])
        cls._GLYPHS['?'] = glyph(['.###.', '#...#', '....#', '...#.', '..#..', '.....', '..#..'])
        cls._GLYPHS['+'] = glyph(['.....', '..#..', '..#..', '#####', '..#..', '..#..', '.....'])

    @classmethod
    def render(cls, text, color):
        cls._init_glyphs()
        text = text.upper()
        w = len(text) * (cls.CHAR_W + 1)
        h = cls.CHAR_H
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))
        cx = 0
        for ch in text:
            gl = cls._GLYPHS.get(ch, cls._GLYPHS['?'])
            for y in range(cls.CHAR_H):
                for x in range(cls.CHAR_W):
                    if gl[y][x]:
                        surf.set_at((cx + x, y), color)
            cx += cls.CHAR_W + 1
        return surf
