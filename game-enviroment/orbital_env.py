"""
orbital_env.py — Ambiente Odisseia Orbital (Pixel Art Retro).
"""

import math
import random
import numpy as np
import pygame
import config as cfg
import physics as phys

# Fonte - estilo arcade
class PixelFont:
    """
    Fonte pixel art 5x7 desenhada manualmente.
    Suporta A-Z, 0-9, e simbolos basicos.
    """

    CHAR_W = 5
    CHAR_H = 7

    _GLYPHS = {}

    @classmethod
    def _init_glyphs(cls):
        if cls._GLYPHS:
            return

        def glyph(rows):
            """Converte lista de strings '.#' em matriz de bools."""
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
        cls._GLYPHS[','] = glyph(['.....', '.....', '.....', '.....', '.....', '..#..', '.#...'])
        cls._GLYPHS['!'] = glyph(['..#..', '..#..', '..#..', '..#..', '..#..', '.....', '..#..'])
        cls._GLYPHS['?'] = glyph(['.###.', '#...#', '....#', '...#.', '..#..', '.....', '..#..'])
        cls._GLYPHS[':'] = glyph(['.....', '..#..', '.....', '.....', '..#..', '.....', '.....'])
        cls._GLYPHS['-'] = glyph(['.....', '.....', '#####', '.....', '.....', '.....', '.....'])
        cls._GLYPHS['+'] = glyph(['.....', '..#..', '..#..', '#####', '..#..', '..#..', '.....'])
        cls._GLYPHS['/'] = glyph(['....#', '...#.', '...#.', '..#..', '.#...', '.#...', '#....'])
        cls._GLYPHS[' '] = glyph(['.....', '.....', '.....', '.....', '.....', '.....', '.....'])
        cls._GLYPHS['['] = glyph(['###..', '#....', '#....', '#....', '#....', '#....', '###..'])
        cls._GLYPHS[']'] = glyph(['..###', '....#', '....#', '....#', '....#', '....#', '..###'])
        cls._GLYPHS['('] = glyph(['...#.', '..#..', '.#...', '.#...', '.#...', '..#..', '...#.'])
        cls._GLYPHS[')'] = glyph(['.#...', '..#..', '...#.', '...#.', '...#.', '..#..', '.#...'])
        cls._GLYPHS['#'] = glyph(['.#.#.', '.#.#.', '#####', '.#.#.', '#####', '.#.#.', '.#.#.'])
        cls._GLYPHS['*'] = glyph(['..#..', '#.#.#', '.##..', '..#..', '.##..', '#.#.#', '..#..'])

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

# OrbitalEnv
class OrbitalEnv:

    def __init__(self, render_mode=None):
        self.render_mode = render_mode

        self.action_space_n = 5
        self.obs_shape = (7,)

        self.planets = [
            {
                "pos": np.array(p["pos"], dtype=np.float64),
                "radius": p["radius"],
                "mass": p["mass"],
                "color": p["color"],
            }
            for p in cfg.PLANETS
        ]

        self.checkpoints = []
        for cp in cfg.CHECKPOINTS:
            self.checkpoints.append({
                "pos": np.array(cp["pos"], dtype=np.float64),
                "radius": cp["radius"],
                "collected": False,
            })

        self.station_pos = np.array(cfg.STATION_POS, dtype=np.float64)
        self.station_radius = cfg.STATION_RADIUS

        self.ship_pos = None
        self.ship_vel = None
        self.fuel = 0.0
        self.done = False
        self.episode_reward = 0.0
        self.episode_steps = 0
        self.last_info = {"status": "not_started"}

        self.trail = []
        self._launch_escaped = False

        self.checkpoint_particles = []

        self.glitch_frames = 0
        self.glitch_active = False

        self.screen = None
        self.canvas = None
        self.clock = None

        if render_mode is not None:
            self._init_pygame()

    # Interface Padrao
    def reset(self):
        self.ship_pos = np.array(cfg.SHIP_START_POS, dtype=np.float64).copy()
        self.ship_vel = np.zeros(2, dtype=np.float64)
        self.fuel = cfg.MAX_FUEL
        self.done = False
        self.episode_reward = 0.0
        self.episode_steps = 0
        self.last_info = {"status": "alive"}

        for cp in self.checkpoints:
            cp["collected"] = False

        self.trail = [tuple(self.ship_pos)]
        self._launch_escaped = False
        self.checkpoint_particles = []
        self.glitch_frames = 0
        self.glitch_active = False

        return self._get_state()

    def step(self, action):
        if self.done:
            return self._get_state(), 0.0, True, self.last_info

        reward = 0.0
        info = {"status": "alive", "checkpoint_collected": False}

        thrust_available = False
        if action != 0 and self.fuel >= cfg.FUEL_COST_PER_THRUST:
            self.fuel -= cfg.FUEL_COST_PER_THRUST
            thrust_available = True
            reward += cfg.REWARD_THRUST_COST

        if self._launch_escaped:
            active_planets = self.planets
        else:
            active_planets = [
                p for i, p in enumerate(self.planets)
                if i != cfg.LAUNCH_PLANET_INDEX
            ]
        grav_accel = phys.total_gravity(self.ship_pos, active_planets, cfg.G)

        if thrust_available:
            thrust_accel = phys.thrust_vector(action, cfg.THRUST_POWER)
        else:
            thrust_accel = np.zeros(2, dtype=np.float64)

        total_accel = grav_accel + thrust_accel

        self.ship_pos, self.ship_vel = phys.apply_kinematics(
            self.ship_pos, self.ship_vel, total_accel, cfg.MAX_SPEED
        )

        self.trail.append(tuple(self.ship_pos))
        if len(self.trail) > cfg.MAX_TRAIL_LENGTH:
            self.trail.pop(0)

        if not self._launch_escaped:
            launch_planet = self.planets[cfg.LAUNCH_PLANET_INDEX]
            dist_to_launch = float(
                np.linalg.norm(self.ship_pos - launch_planet["pos"])
            )
            if dist_to_launch > cfg.LAUNCH_ESCAPE_DISTANCE:
                self._launch_escaped = True

        for i, planet in enumerate(self.planets):
            if not self._launch_escaped and i == cfg.LAUNCH_PLANET_INDEX:
                continue
            if phys.check_circle_collision(
                self.ship_pos, cfg.SHIP_RADIUS,
                planet["pos"], planet["radius"],
            ):
                self._trigger_glitch()
                reward = cfg.REWARD_FAILURE_COLLISION
                self.done = True
                info["status"] = "crashed_planet"
                info["planet_mass"] = planet["mass"]
                self.last_info = info
                self.episode_reward += reward
                return self._get_state(), reward, True, info

        if phys.is_out_of_bounds(
            self.ship_pos, cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT
        ):
            self._trigger_glitch()
            reward = cfg.REWARD_FAILURE_OOB
            self.done = True
            info["status"] = "out_of_bounds"
            self.last_info = info
            self.episode_reward += reward
            return self._get_state(), reward, True, info

        for cp in self.checkpoints:
            if cp["collected"]:
                continue
            if phys.check_circle_collision(
                self.ship_pos, cfg.SHIP_RADIUS,
                cp["pos"], cp["radius"],
            ):
                cp["collected"] = True
                self.fuel = min(self.fuel + cfg.FUEL_PICKUP, cfg.MAX_FUEL)
                reward += cfg.REWARD_CHECKPOINT
                info["checkpoint_collected"] = True
                self._spawn_checkpoint_burst((
                    float(cp["pos"][0]), float(cp["pos"][1])
                ))

        station_center = (
            float(self.station_pos[0]),
            float(self.station_pos[1]),
        )
        if phys.check_circle_rect_collision(
            self.ship_pos, cfg.SHIP_RADIUS,
            station_center, cfg.STATION_WIDTH, cfg.STATION_HEIGHT,
        ):
            reward += cfg.REWARD_SUCCESS + self.fuel * cfg.REWARD_FUEL_BONUS_FACTOR
            self.done = True
            info["status"] = "docked"
            self.last_info = info
            self.episode_reward += reward
            return self._get_state(), reward, True, info

        if self.fuel <= 0.0:
            reward = cfg.REWARD_FAILURE_NO_FUEL
            self.done = True
            info["status"] = "no_fuel"
            self.last_info = info
            self.episode_reward += reward
            return self._get_state(), reward, True, info

        reward += cfg.REWARD_STEP

        self.episode_reward += reward
        self.episode_steps += 1
        self.last_info = info

        return self._get_state(), reward, self.done, info

    def _get_state(self):
        checkpoint_dist = 0.0
        for cp in self.checkpoints:
            if not cp["collected"]:
                checkpoint_dist = float(np.linalg.norm(self.ship_pos - cp["pos"]))
                break
        station_dist = float(np.linalg.norm(self.ship_pos - self.station_pos))
        return np.array([
            float(self.ship_pos[0]), float(self.ship_pos[1]),
            float(self.ship_vel[0]), float(self.ship_vel[1]),
            float(self.fuel), checkpoint_dist, station_dist,
        ], dtype=np.float64)

    # Renderizacao
    def render(self):
        if self.canvas is None:
            self._init_pygame()

        glitch_offset = 0
        if self.glitch_active and self.glitch_frames > 0:
            glitch_offset = random.randint(
                -cfg.GLITCH_OFFSET_MAX, cfg.GLITCH_OFFSET_MAX
            )
            self.glitch_frames -= 1
            if self.glitch_frames <= 0:
                self.glitch_active = False

        self.canvas.fill(cfg.COLOR_SPACE)

        self._draw_grid()
        self._draw_starfield()
        self._draw_trail()
        self._draw_planets()
        self._draw_checkpoints()
        self._draw_station()
        self._draw_launch_indicator()
        self._update_particles()
        self._draw_particles()
        self._draw_ship()
        self._draw_hud()

        if self.done:
            self._draw_status_overlay()

        if glitch_offset != 0:
            temp = self.canvas.copy()
            self.canvas.fill(cfg.COLOR_SPACE)
            self.canvas.blit(temp, (glitch_offset, 0))

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

    # Inicializacao Pygame
    def _init_pygame(self):
        if self.screen is not None:
            return
        pygame.init()
        self.screen = pygame.display.set_mode(
            (cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT)
        )
        pygame.display.set_caption("Odisseia Orbital")
        self.canvas = pygame.Surface(
            (cfg.RENDER_WIDTH, cfg.RENDER_HEIGHT)
        )
        self.clock = pygame.time.Clock()
        self._generate_stars()

    # Plano de fundo
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
                sx = star["x"]
                sy = star["y"]
                if 0 <= sx < cfg.RENDER_WIDTH and 0 <= sy < cfg.RENDER_HEIGHT:
                    self.canvas.set_at((sx, sy), star["color"])

    # Rastro do foguete
    def _draw_trail(self):
        trail_spacing = 3
        for idx in range(0, len(self.trail), trail_spacing):
            p = self.trail[idx]
            rx = int(p[0] * cfg.RENDER_WIDTH / cfg.SCREEN_WIDTH)
            ry = int(p[1] * cfg.RENDER_HEIGHT / cfg.SCREEN_HEIGHT)
            if 2 <= rx < cfg.RENDER_WIDTH - 2 and 2 <= ry < cfg.RENDER_HEIGHT - 2:
                pygame.draw.rect(self.canvas, cfg.COLOR_CYAN,
                                 (rx - 1, ry - 1, 3, 3))

    # Planetas
    def _draw_planets(self):
        for i, planet in enumerate(self.planets):
            scale = cfg.RENDER_WIDTH / cfg.SCREEN_WIDTH
            px = int(planet["pos"][0] * scale)
            py = int(planet["pos"][1] * scale)
            radius = int(planet["radius"] * scale)
            color = planet["color"]

            if i == cfg.LAUNCH_PLANET_INDEX:
                self._draw_launch_planet(px, py, radius, color)
                continue

            if i == 1:
                self._draw_giant(px, py, radius, color)
            elif i == 2:
                self._draw_crystal(px, py, radius, color)
            elif i in (3, 5):
                self._draw_gas(px, py, radius, color, i)
            elif i == 4:
                self._draw_rocky(px, py, radius, color)

            self._draw_circle(self.canvas, px, py, radius, color)
            self._draw_circle(self.canvas, px, py, radius, cfg.COLOR_BLACK, 2)

    def _draw_circle(self, surf, cx, cy, r, color, width=0):
        pygame.draw.circle(surf, color, (cx, cy), r, width)

    def _draw_giant(self, px, py, radius, color):
        for y in range(py - radius, py + radius + 1):
            dx = int(math.sqrt(max(0, radius * radius - (y - py) * (y - py))))
            if dx > 0:
                for x in range(px - dx, px + dx + 1):
                    shade = (x + y) % 5
                    if shade == 0:
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

    def _draw_crystal(self, px, py, radius, color):
        sides = 6
        pts = []
        for j in range(sides):
            angle = j * (2 * math.pi / sides) - math.pi / 2
            pts.append((
                int(px + radius * math.cos(angle)),
                int(py + radius * math.sin(angle)),
            ))
        if len(pts) >= 3:
            pygame.draw.polygon(self.canvas, color, pts)
            pygame.draw.polygon(self.canvas, cfg.COLOR_BLACK, pts, 2)

        for j in range(3):
            pygame.draw.line(self.canvas, cfg.COLOR_WHITE,
                             pts[j], pts[j + 3], 1)

        flash = (pygame.time.get_ticks() // 200) % 2
        if flash:
            brighter = tuple(min(255, v + 60) for v in color)
            pygame.draw.circle(self.canvas, brighter, (px, py), max(2, radius // 3))

    def _draw_gas(self, px, py, radius, color, planet_idx):
        band_count = 5
        band_h = radius * 2 // band_count
        lighter = tuple(min(255, v + 40) for v in color)
        darker = tuple(max(0, v - 40) for v in color)

        for band in range(band_count):
            by = py - radius + band * band_h
            for y in range(by, by + band_h + 1):
                dx = int(math.sqrt(max(0, radius * radius - (y - py) * (y - py))))
                band_color = lighter if band % 2 == 0 else darker
                for x in range(px - dx, px + dx + 1):
                    self.canvas.set_at((x, y), band_color)

        if planet_idx == 3:
            spot_x = px + radius // 4
            spot_y = py - radius // 4
            spot_r = max(3, radius // 4)
            pygame.draw.ellipse(self.canvas, cfg.COLOR_CYAN,
                                (spot_x - spot_r, spot_y - spot_r // 2,
                                 spot_r * 2, spot_r), 1)
        else:
            cur_x = px - radius // 2
            cur_y = py
            for _ in range(4):
                pygame.draw.circle(self.canvas, cfg.COLOR_BROWN,
                                   (cur_x, cur_y), max(2, radius // 5), 1)
                cur_x += radius // 3
                cur_y += random.choice([-1, 1]) * radius // 4

    def _draw_rocky(self, px, py, radius, color):
        for y in range(py - radius, py + radius + 1):
            dx = int(math.sqrt(max(0, radius * radius - (y - py) * (y - py))))
            if dx > 0:
                for x in range(px - dx, px + dx + 1):
                    rng = abs(x - px) + abs(y - py)
                    if rng % 7 < 3:
                        c = tuple(max(0, v - 25) for v in color)
                        self.canvas.set_at((x, y), c)

        craters = [
            (px - radius // 3, py - radius // 4, radius // 4),
            (px + radius // 3, py - radius // 4, radius // 5),
            (px + radius // 4, py + radius // 3, radius // 5),
            (px - radius // 4, py + radius // 4, radius // 6),
        ]
        for cx, cy, cr in craters:
            pygame.draw.circle(self.canvas, cfg.COLOR_BROWN, (cx, cy), cr)
            pygame.draw.circle(self.canvas, tuple(min(255, v + 50) for v in color),
                               (cx, cy), cr, 1)

        wx = px - radius // 3
        wy = py - radius // 3
        pygame.draw.rect(self.canvas, cfg.COLOR_WHITE,
                         (wx - 2, wy - 2, 4, 4))

    def _draw_launch_planet(self, px, py, radius, color):
        start_angle = -math.pi / 3
        end_angle = math.pi / 3
        num_points = 16
        pts = [(px, py)]
        for j in range(num_points + 1):
            angle = start_angle + (end_angle - start_angle) * j / num_points
            pts.append((
                int(px + radius * math.cos(angle)),
                int(py + radius * math.sin(angle)),
            ))
        pygame.draw.polygon(self.canvas, color, pts)

        self._draw_circle(self.canvas, px, py, radius, cfg.COLOR_BLACK, 2)

        plat_x = px + radius - 6
        plat_y = py - 8
        pygame.draw.rect(self.canvas, cfg.COLOR_GRAY,
                         (plat_x, plat_y, 6, 8))
        pygame.draw.rect(self.canvas, cfg.COLOR_WHITE,
                         (plat_x, plat_y, 6, 8), 1)
        pygame.draw.rect(self.canvas, cfg.COLOR_CYAN,
                         (plat_x + 2, plat_y + 2, 2, 2))

    # Checkpoints
    def _draw_checkpoints(self):
        current_time = pygame.time.get_ticks()
        scale = cfg.RENDER_WIDTH / cfg.SCREEN_WIDTH
        pulse = (current_time // 200) % 2

        for cp in self.checkpoints:
            if cp["collected"]:
                continue

            cx = int(cp["pos"][0] * scale)
            cy = int(cp["pos"][1] * scale)
            size = int(cp["radius"] * scale * 0.7)

            cp_color = cfg.COLOR_YELLOW if pulse else cfg.COLOR_GOLD
            dark = cfg.COLOR_BLACK

            diamond = [
                (cx, cy - size),
                (cx + size, cy),
                (cx, cy + size),
                (cx - size, cy),
            ]
            pygame.draw.polygon(self.canvas, cp_color, diamond)
            pygame.draw.polygon(self.canvas, dark, diamond, 1)

            inner_s = max(2, size // 2)
            inner = [
                (cx, cy - inner_s),
                (cx + inner_s, cy),
                (cx, cy + inner_s),
                (cx - inner_s, cy),
            ]
            pygame.draw.polygon(self.canvas, dark, inner)

    # Estacao final
    def _draw_station(self):
        scale = cfg.RENDER_WIDTH / cfg.SCREEN_WIDTH
        sx = int(self.station_pos[0] * scale)
        sy = int(self.station_pos[1] * scale)
        hw = int(cfg.STATION_WIDTH * scale) // 2
        hh = int(cfg.STATION_HEIGHT * scale) // 2
        current_time = pygame.time.get_ticks()

        if self.ship_pos is not None:
            dist = float(np.linalg.norm(self.ship_pos - self.station_pos))
            if dist < 150:
                sxs = int(self.ship_pos[0] * scale)
                sys = int(self.ship_pos[1] * scale)
                dx = sx - sxs
                dy = sy - sys
                steps = int(dist / 8)
                for d in range(steps):
                    t = d / max(steps, 1)
                    if d % 2 == 0:
                        px = int(sxs + dx * t)
                        py = int(sys + dy * t)
                        if 0 <= px < cfg.RENDER_WIDTH and 0 <= py < cfg.RENDER_HEIGHT:
                            self.canvas.set_at((px, py), cfg.COLOR_CYAN)

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

        dock_on = (current_time // 300) % 2
        dock_color = cfg.COLOR_GREEN if dock_on else cfg.COLOR_DARK_GRAY
        pygame.draw.rect(self.canvas, dock_color, (sx - 2, sy - 2, 5, 5))
        pygame.draw.rect(self.canvas, cfg.COLOR_BLACK, (sx - 3, sy - 3, 7, 7), 1)

    # Nave espacial
    def _draw_ship(self):
        scale = cfg.RENDER_WIDTH / cfg.SCREEN_WIDTH
        x = self.ship_pos[0] * scale
        y = self.ship_pos[1] * scale
        vx, vy = float(self.ship_vel[0]), float(self.ship_vel[1])

        speed = math.hypot(vx, vy)
        if speed > 0.05:
            angle = math.atan2(vy, vx)
        else:
            angle = 0.0

        size = 7

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
        pygame.draw.polygon(self.canvas, cfg.COLOR_WHITE, pts)
        pygame.draw.polygon(self.canvas, cfg.COLOR_BLACK, pts, 1)
        pygame.draw.polygon(self.canvas, cfg.COLOR_CYAN, pts, 1)

        cockpit_x = int(x + size * 0.3 * math.cos(angle))
        cockpit_y = int(y + size * 0.3 * math.sin(angle))
        pygame.draw.rect(self.canvas, cfg.COLOR_CYAN,
                         (cockpit_x - 1, cockpit_y - 1, 3, 3))

    # Particulas (checkpoint burst)
    def _spawn_checkpoint_burst(self, pos):
        if self.render_mode is None:
            return
        scale = cfg.RENDER_WIDTH / cfg.SCREEN_WIDTH
        cx = pos[0] * scale
        cy = pos[1] * scale
        for _ in range(cfg.MAX_CHECKPOINT_PARTICLES):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(0.5, 2.5)
            self.checkpoint_particles.append({
                "x": cx,
                "y": cy,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "life": cfg.CHECKPOINT_PARTICLE_LIFETIME,
                "max_life": cfg.CHECKPOINT_PARTICLE_LIFETIME,
                "color": random.choice([
                    cfg.COLOR_YELLOW, cfg.COLOR_GOLD, cfg.COLOR_WHITE
                ]),
            })

    def _update_particles(self):
        for p in self.checkpoint_particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= 1
        self.checkpoint_particles = [
            p for p in self.checkpoint_particles if p["life"] > 0
        ]

    def _draw_particles(self):
        for p in self.checkpoint_particles:
            t = p["life"] / p["max_life"]
            px = int(p["x"])
            py = int(p["y"])
            if t > 0.2 and 0 <= px < cfg.RENDER_WIDTH and 0 <= py < cfg.RENDER_HEIGHT:
                self.canvas.set_at((px, py), p["color"])

    # Indicador de Lancamento
    def _draw_launch_indicator(self):
        if self._launch_escaped:
            return

        scale = cfg.RENDER_WIDTH / cfg.SCREEN_WIDTH
        lp = self.planets[cfg.LAUNCH_PLANET_INDEX]
        px = int(lp["pos"][0] * scale) + int(lp["radius"] * scale) + 6
        py = int(lp["pos"][1] * scale) - int(lp["radius"] * scale) - 10

        label = PixelFont.render("LAUNCH", cfg.COLOR_MAGENTA)
        self.canvas.blit(label, (px, py))

        current_time = pygame.time.get_ticks()
        arrow_on = (current_time // 250) % 2
        if arrow_on:
            for j in range(3):
                ax = px + j * 4
                ay = py + 10
                if 0 <= ax < cfg.RENDER_WIDTH - 4 and 0 <= ay < cfg.RENDER_HEIGHT:
                    pygame.draw.rect(self.canvas, cfg.COLOR_CYAN,
                                     (ax, ay, 4, 2))

    # HUD — distribuido sem caixa
    def _draw_hud(self):
        current_time = pygame.time.get_ticks()

        danger, danger_dist = self._check_danger()

        self._draw_hud_top_left(current_time)
        self._draw_hud_top_right(current_time)
        self._draw_hud_top_warning(danger, danger_dist, current_time)
        self._draw_hud_fuel_bar()
        self._draw_hud_distance()

    def _check_danger(self):
        danger = False
        danger_dist = 999
        if self.ship_pos is not None and self._launch_escaped:
            for i, planet in enumerate(self.planets):
                if i == cfg.LAUNCH_PLANET_INDEX:
                    continue
                d = float(np.linalg.norm(self.ship_pos - planet["pos"]))
                if d < planet["radius"] + 60:
                    danger = True
                    danger_dist = min(danger_dist, d - planet["radius"])
        return danger, danger_dist

    def _blit_text(self, surf, text, x, y, color):
        rendered = PixelFont.render(text, color)
        for ox, oy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
            shadow = PixelFont.render(text, cfg.COLOR_BLACK)
            if 0 <= x + ox < cfg.RENDER_WIDTH and 0 <= y + oy < cfg.RENDER_HEIGHT:
                self.canvas.blit(shadow, (x + ox, y + oy))
        self.canvas.blit(rendered, (x, y))
        return rendered.get_width(), rendered.get_height()

    def _draw_hud_top_left(self, current_time):
        x, y = 4, 4
        self._blit_text(self.canvas, f"PTS {self.episode_reward:+.0f}", x, y, cfg.COLOR_CYAN)
        w, _ = self._blit_text(self.canvas, f"C {self.episode_steps}", x, y + 10, cfg.COLOR_GRAY)

    def _draw_hud_top_right(self, current_time):
        collected = sum(1 for cp in self.checkpoints if cp["collected"])
        total = len(self.checkpoints)
        x = cfg.RENDER_WIDTH - 80
        y = 4

        self._blit_text(self.canvas, "CP", x, y, cfg.COLOR_WHITE)

        diamond_size = 3
        dx = x + 20
        dy = y + 3
        for i in range(total):
            cx = dx + i * 9
            diamond = [
                (cx, dy - diamond_size),
                (cx + diamond_size, dy),
                (cx, dy + diamond_size),
                (cx - diamond_size, dy),
            ]
            if i < collected:
                pygame.draw.polygon(self.canvas, cfg.COLOR_YELLOW, diamond)
                pygame.draw.polygon(self.canvas, cfg.COLOR_BLACK, diamond, 1)
            else:
                pygame.draw.polygon(self.canvas, cfg.COLOR_DARK_GRAY, diamond, 1)

    def _draw_hud_top_warning(self, danger, danger_dist, current_time):
        if not danger:
            return

        blink = (current_time // 250) % 2
        if not blink:
            return

        msg = f"WARNING"
        rendered = PixelFont.render(msg, cfg.COLOR_RED)
        x = (cfg.RENDER_WIDTH - rendered.get_width()) // 2
        y = 4
        for ox, oy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
            shadow = PixelFont.render(msg, cfg.COLOR_BLACK)
            self.canvas.blit(shadow, (x + ox, y + oy))
        self.canvas.blit(rendered, (x, y))

    def _draw_hud_fuel_bar(self):
        block_count = cfg.HUD_FUEL_BLOCKS
        block_w = 8
        block_h = 6
        gap = 2
        total_w = block_count * block_w + (block_count - 1) * gap
        x = 6
        y = cfg.RENDER_HEIGHT - block_h - 8

        fuel_label = PixelFont.render("FUEL", cfg.COLOR_WHITE)
        for ox, oy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
            shadow = PixelFont.render("FUEL", cfg.COLOR_BLACK)
            self.canvas.blit(shadow, (x - 1 + ox, y - 9 + oy))
        self.canvas.blit(fuel_label, (x, y - 10))

        bx = x + 30
        fuel_ratio = self.fuel / cfg.MAX_FUEL
        filled = int(block_count * fuel_ratio)
        for b in range(block_count):
            bpx = bx + b * (block_w + gap)
            bpy = y
            if b < filled:
                if b >= 7:
                    bc = cfg.COLOR_GREEN
                elif b >= 4:
                    bc = cfg.COLOR_YELLOW
                else:
                    bc = cfg.COLOR_RED
                pygame.draw.rect(self.canvas, bc, (bpx, bpy, block_w, block_h))
            pygame.draw.rect(self.canvas, cfg.COLOR_DARK_GRAY,
                             (bpx, bpy, block_w, block_h), 1)

        fuel_text = PixelFont.render(f"{int(self.fuel)}", cfg.COLOR_WHITE)
        tx = bx + total_w + 6
        for ox, oy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
            shadow = PixelFont.render(f"{int(self.fuel)}", cfg.COLOR_BLACK)
            self.canvas.blit(shadow, (tx - 1 + ox, y - 1 + oy))
        self.canvas.blit(fuel_text, (tx, y - 1))

    def _draw_hud_distance(self):
        if self.ship_pos is None:
            return

        station_dist = float(np.linalg.norm(self.ship_pos - self.station_pos))
        dist_pw = 56
        dist_ph = 56
        dist_x = cfg.RENDER_WIDTH - dist_pw - 6
        dist_y = cfg.RENDER_HEIGHT - dist_ph - 6

        pygame.draw.rect(self.canvas, cfg.COLOR_BLACK, (dist_x, dist_y, dist_pw, dist_ph))
        pygame.draw.rect(self.canvas, cfg.COLOR_CYAN, (dist_x, dist_y, dist_pw, dist_ph), 2)

        dist_label = PixelFont.render("DST", cfg.COLOR_WHITE)
        self.canvas.blit(dist_label,
                         (dist_x + (dist_pw - dist_label.get_width()) // 2, dist_y + 4))

        dist_val = PixelFont.render(f"{int(station_dist)}", cfg.COLOR_CYAN)
        self.canvas.blit(dist_val,
                         (dist_x + (dist_pw - dist_val.get_width()) // 2, dist_y + 18))

        bar_h = dist_ph - 28
        bar_x = dist_x + dist_pw // 2 - 2
        bar_y = dist_y + 24
        max_dist = math.hypot(cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT)
        dist_ratio = min(1.0, station_dist / max_dist)
        filled_h = int(bar_h * (1.0 - dist_ratio))
        pygame.draw.rect(self.canvas, cfg.COLOR_DARK_GRAY,
                         (bar_x, bar_y, 4, bar_h), 1)
        if filled_h > 0:
            bar_color = cfg.COLOR_GREEN if dist_ratio < 0.3 else (
                cfg.COLOR_YELLOW if dist_ratio < 0.6 else cfg.COLOR_RED
            )
            pygame.draw.rect(self.canvas, bar_color,
                             (bar_x, bar_y + bar_h - filled_h, 4, filled_h))

    # Status Overlay
    def _draw_status_overlay(self):
        status = self.last_info.get("status", "unknown")
        current_time = pygame.time.get_ticks()

        messages = {
            "docked": ("MISSION COMPLETE", cfg.COLOR_GREEN),
            "crashed_planet": ("GAME OVER", cfg.COLOR_RED),
            "out_of_bounds": ("SIGNAL LOST", cfg.COLOR_RED),
            "no_fuel": ("NO FUEL", cfg.COLOR_RED),
        }
        msg, color = messages.get(status, ("MISSION END", cfg.COLOR_WHITE))

        sub_msgs = {
            "docked": "STATION REACHED",
            "crashed_planet": "PLANET COLLISION",
            "out_of_bounds": "OUT OF ORBIT",
            "no_fuel": "FUEL DEPLETED",
        }
        sub_msg = sub_msgs.get(status, "")

        overlay = pygame.Surface((cfg.RENDER_WIDTH, cfg.RENDER_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.canvas.blit(overlay, (0, 0))

        frame_w = 280
        frame_h = 120
        frame_x = (cfg.RENDER_WIDTH - frame_w) // 2
        frame_y = (cfg.RENDER_HEIGHT - frame_h) // 2

        pygame.draw.rect(self.canvas, cfg.COLOR_BLACK,
                         (frame_x, frame_y, frame_w, frame_h))
        pygame.draw.rect(self.canvas, color,
                         (frame_x, frame_y, frame_w, frame_h), 2)
        pygame.draw.rect(self.canvas, cfg.COLOR_BLACK,
                         (frame_x + 2, frame_y + 2, frame_w - 4, frame_h - 4), 1)

        glitch_off = 0
        if status != "docked":
            glitch_off = random.randint(-1, 1)

        title = PixelFont.render(msg, color)
        tx = frame_x + (frame_w - title.get_width()) // 2 + glitch_off
        ty = frame_y + 16
        self.canvas.blit(title, (tx, ty))

        if sub_msg:
            sub = PixelFont.render(sub_msg, cfg.COLOR_WHITE)
            sx2 = frame_x + (frame_w - sub.get_width()) // 2
            self.canvas.blit(sub, (sx2, ty + 20))

        collected = sum(1 for cp in self.checkpoints if cp["collected"])
        stats = PixelFont.render(
            f"PTS:{self.episode_reward:+.0f} C:{self.episode_steps} CP:{collected}/{len(self.checkpoints)}",
            cfg.COLOR_CYAN,
        )
        self.canvas.blit(stats,
                         (frame_x + (frame_w - stats.get_width()) // 2, frame_y + frame_h - 36))

        blink = (current_time // 500) % 2
        if blink:
            hint = PixelFont.render("PRESS [R] TO RETRY", cfg.COLOR_YELLOW)
            self.canvas.blit(hint,
                             (frame_x + (frame_w - hint.get_width()) // 2,
                              frame_y + frame_h - 18))

    # Glitch
    def _trigger_glitch(self):
        self.glitch_active = True
        self.glitch_frames = cfg.GLITCH_DURATION