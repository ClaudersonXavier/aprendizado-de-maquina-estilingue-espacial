import math
import random
import numpy as np
import pygame
import config as cfg
import physics as phys
from .ship import NaveGenetica


class AmbienteGenetico:

    def __init__(self, pop_size=100, render_mode=None):
        self.pop_size = pop_size
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

        self.checkpoints = []
        for cp in cfg.CHECKPOINTS:
            self.checkpoints.append({
                "pos": np.array(cp["pos"], dtype=np.float64),
                "radius": cp["radius"],
                "collected": False,
            })

        self.station_pos = np.array(cfg.STATION_POS, dtype=np.float64)
        self.station_radius = cfg.STATION_RADIUS

        self.frota = []
        self.episode_steps = 0
        self.total_alive = 0
        self.total_docked = 0
        self.total_crashed = 0
        self.total_oob = 0
        self.total_no_fuel = 0
        self.generation = 1

        self.screen = None
        self.canvas = None
        self.clock = None

        if render_mode is not None:
            self._init_pygame()

        self._criar_frota()

    def _criar_frota(self):
        self.frota = []
        for _ in range(self.pop_size):
            self.frota.append(NaveGenetica(*cfg.SHIP_START_POS))
        self.total_alive = self.pop_size
        self.total_docked = 0
        self.total_crashed = 0
        self.total_oob = 0
        self.total_no_fuel = 0

    def reset(self):
        self.episode_steps = 0

        for nave in self.frota:
            nave.reiniciar(*cfg.SHIP_START_POS)

        self.total_alive = self.pop_size
        self.total_docked = 0
        self.total_crashed = 0
        self.total_oob = 0
        self.total_no_fuel = 0

    def step(self, actions_list):
        self.episode_steps += 1

        for idx, nave in enumerate(self.frota):
            if not nave.ativa:
                continue

            action = actions_list[idx] if idx < len(actions_list) else 0

            nave.steps_alive += 1

            if action != 0 and nave.fuel >= cfg.FUEL_COST_PER_THRUST:
                nave.fuel -= cfg.FUEL_COST_PER_THRUST
                thrust_available = True
            else:
                thrust_available = False

            if nave._launch_escaped:
                active_planets = self.planets
            else:
                active_planets = [
                    p for i, p in enumerate(self.planets)
                    if i != cfg.LAUNCH_PLANET_INDEX
                ]
            grav_accel = phys.total_gravity(nave.pos, active_planets, cfg.G)

            if thrust_available:
                thrust_accel = phys.thrust_vector(action, cfg.THRUST_POWER)
            else:
                thrust_accel = np.zeros(2, dtype=np.float64)

            total_accel = grav_accel + thrust_accel

            nave.pos, nave.vel = phys.apply_kinematics(
                nave.pos, nave.vel, total_accel, cfg.MAX_SPEED
            )

            nave.trail.append(tuple(nave.pos))
            if len(nave.trail) > cfg.MAX_TRAIL_LENGTH:
                nave.trail.pop(0)

            if not nave._launch_escaped:
                launch_planet = self.planets[cfg.LAUNCH_PLANET_INDEX]
                dist_to_launch = float(
                    np.linalg.norm(nave.pos - launch_planet["pos"])
                )
                if dist_to_launch > cfg.LAUNCH_ESCAPE_DISTANCE:
                    nave._launch_escaped = True

            crashed = False
            for i, planet in enumerate(self.planets):
                if phys.check_circle_collision(
                    nave.pos, cfg.SHIP_RADIUS,
                    planet["pos"], planet["radius"],
                ):
                    nave.ativa = False
                    nave.status = "crashed"
                    self.total_crashed += 1
                    self.total_alive -= 1
                    crashed = True
                    break

            if crashed:
                continue

            if phys.is_out_of_bounds(
                nave.pos, cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT
            ):
                nave.ativa = False
                nave.status = "oob"
                self.total_oob += 1
                self.total_alive -= 1
                continue

            alvo_min = self.station_pos
            if nave._alvo_travado is not None and not nave.checkpoints_visitados[nave._alvo_travado]:
                alvo_min = self.checkpoints[nave._alvo_travado]["pos"]
            else:
                melhor_d = float('inf')
                for idx, cp in enumerate(self.checkpoints):
                    if not nave.checkpoints_visitados[idx]:
                        d = float(np.linalg.norm(cp["pos"] - nave.pos))
                        if d < melhor_d:
                            melhor_d = d
                            alvo_min = cp["pos"]
            d_alvo = float(np.linalg.norm(alvo_min - nave.pos))
            if d_alvo < nave._min_dist_alvo:
                nave._min_dist_alvo = d_alvo

            for idx_cp, cp in enumerate(self.checkpoints):
                if nave.checkpoints_visitados[idx_cp]:
                    continue
                if phys.check_circle_collision(
                    nave.pos, cfg.SHIP_RADIUS,
                    cp["pos"], cp["radius"],
                ):
                    nave.checkpoints_visitados[idx_cp] = True
                    nave.checkpoints_coletados += 1
                    nave.fuel = min(nave.fuel + cfg.FUEL_PICKUP, cfg.MAX_FUEL)

            station_center = (
                float(self.station_pos[0]),
                float(self.station_pos[1]),
            )
            if nave.checkpoints_coletados == len(self.checkpoints):
                if phys.check_circle_rect_collision(
                    nave.pos, cfg.SHIP_RADIUS,
                    station_center, cfg.STATION_WIDTH, cfg.STATION_HEIGHT,
                ):
                    nave.ativa = False
                    nave.status = "docked"
                    self.total_docked += 1
                    self.total_alive -= 1
                    continue

            if nave.fuel <= 0.0:
                nave.ativa = False
                nave.status = "no_fuel"
                self.total_no_fuel += 1
                self.total_alive -= 1
                continue

        return self.total_alive

    def obter_sensores_nave(self, nave):
        if nave._alvo_travado is not None and nave.checkpoints_visitados[nave._alvo_travado]:
            nave._alvo_travado = None

        if nave._alvo_travado is None:
            melhor_dist = float('inf')
            for idx, cp in enumerate(self.checkpoints):
                if not nave.checkpoints_visitados[idx]:
                    d = float(np.linalg.norm(cp["pos"] - nave.pos))
                    if d < melhor_dist:
                        melhor_dist = d
                        nave._alvo_travado = idx

        if nave._alvo_travado is not None:
            alvo_pos = self.checkpoints[nave._alvo_travado]["pos"]
        else:
            alvo_pos = self.station_pos

        dx = float(alvo_pos[0] - nave.pos[0])
        dy = float(alvo_pos[1] - nave.pos[1])
        vx = float(nave.vel[0])
        vy = float(nave.vel[1])
        fuel = float(nave.fuel)

        danger_dist = 999.0
        danger_dx = 0.0
        danger_dy = 0.0
        perigos = []
        for i, planet in enumerate(self.planets):
            if not nave._launch_escaped and i == cfg.LAUNCH_PLANET_INDEX:
                continue
            dist = float(np.linalg.norm(nave.pos - planet["pos"]))
            surface_dist = dist - planet["radius"]
            p_dx = float(planet["pos"][0] - nave.pos[0])
            p_dy = float(planet["pos"][1] - nave.pos[1])
            perigos.append((surface_dist, p_dx, p_dy))

        perigos.sort(key=lambda x: x[0])
        p1 = perigos[0] if len(perigos) > 0 else (999.0, 0.0, 0.0)
        p2 = perigos[1] if len(perigos) > 1 else (999.0, 0.0, 0.0)

        dist_alvo = max(math.hypot(dx, dy), 1.0)
        vel_toward = (vx * dx + vy * dy) / dist_alvo
        vel_toward /= 2.75

        return [dx, dy, vx, vy, fuel,
                p1[0], p1[1], p1[2],
                p2[0], p2[1], p2[2],
                vel_toward]

    def calcular_fitness_frota(self):
        for nave in self.frota:
            n = nave.checkpoints_coletados

            score_garantido = 20000.0 * n

            alvo_pos = self.station_pos
            if nave._alvo_travado is not None and not nave.checkpoints_visitados[nave._alvo_travado]:
                alvo_pos = self.checkpoints[nave._alvo_travado]["pos"]
            elif n < len(self.checkpoints):
                melhor_dist = float('inf')
                for idx, cp in enumerate(self.checkpoints):
                    if not nave.checkpoints_visitados[idx]:
                        d = float(np.linalg.norm(cp["pos"] - nave.pos))
                        if d < melhor_dist:
                            melhor_dist = d
                            alvo_pos = cp["pos"]

            start_pos = np.array(cfg.SHIP_START_POS, dtype=np.float64)
            dist_inicial = float(np.linalg.norm(alvo_pos - start_pos))
            ratio = max(0.0, 1.0 - nave._min_dist_alvo / max(dist_inicial, 1.0))

            mult = 1.0 + n * 0.5
            score_exploracao = ratio * 10000.0 * mult
            score_exploracao += (nave.fuel / cfg.MAX_FUEL) * 4000.0 * mult

            if n == 0:
                score_exploracao -= nave.steps_alive * 1.0

            if nave.status == "docked":
                score_garantido += 200000.0 + nave.fuel * 100.0
            elif nave.status == "crashed":
                score_exploracao *= 0.1
            elif nave.status == "oob":
                score_exploracao *= 0.02
            elif nave.status == "no_fuel":
                score_exploracao *= 0.3

            nave.fitness = max(1.0, score_garantido + score_exploracao)

    def evoluir_geracao(self, taxa_mutacao=0.05, forca_mutacao=0.15, pct_renovacao=0.0):
        frota_ordenada = sorted(self.frota, key=lambda n: n.fitness, reverse=True)
        novos_dnas = []

        elites = frota_ordenada[:10]
        for elite in elites:
            novos_dnas.append(elite.cerebro.obter_cromossomo())

        tamanho_crom = len(novos_dnas[0])
        tamanho_frota = len(self.frota)

        qtd_renovacao = int(tamanho_frota * pct_renovacao)
        qtd_cruzamento = tamanho_frota - qtd_renovacao

        pesos_rank = [(tamanho_frota - i) ** 2 for i in range(tamanho_frota)]
        soma_pesos = sum(pesos_rank)

        def _sortear_por_rank():
            ponto = random.uniform(0, soma_pesos)
            soma_atual = 0.0
            for idx, nave in enumerate(frota_ordenada):
                soma_atual += pesos_rank[idx]
                if soma_atual >= ponto:
                    return nave
            return frota_ordenada[-1]

        while len(novos_dnas) < qtd_cruzamento:
            pai = _sortear_por_rank()
            mae = _sortear_por_rank()
            tentativas = 0
            while mae is pai and tentativas < 10:
                mae = _sortear_por_rank()
                tentativas += 1

            dna_pai = pai.cerebro.obter_cromossomo()
            dna_mae = mae.cerebro.obter_cromossomo()

            mascara = np.random.rand(tamanho_crom) < 0.5
            dna_filho = np.where(mascara, dna_pai, dna_mae)

            for i in range(len(dna_filho)):
                if random.random() < taxa_mutacao:
                    dna_filho[i] += np.random.randn() * forca_mutacao

            novos_dnas.append(dna_filho)

        from .ship import CerebroNave
        while len(novos_dnas) < tamanho_frota:
            novo_cerebro = CerebroNave()
            novos_dnas.append(novo_cerebro.obter_cromossomo())

        for nave, dna in zip(self.frota, novos_dnas):
            nave.cerebro.definir_cromossomo(dna)

        self.generation += 1

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
        self._draw_fleet_hud()

        scaled = pygame.transform.scale(
            self.canvas, (cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT)
        )
        self.screen.blit(scaled, (0, 0))
        pygame.display.flip()
        self.clock.tick(cfg.FPS)

    def _init_pygame(self):
        if self.screen is not None:
            return
        pygame.init()
        self.screen = pygame.display.set_mode(
            (cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT)
        )
        pygame.display.set_caption("Odisseia Orbital — Algoritmo Genetico")
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
                sx = star["x"]
                sy = star["y"]
                if 0 <= sx < cfg.RENDER_WIDTH and 0 <= sy < cfg.RENDER_HEIGHT:
                    self.canvas.set_at((sx, sy), star["color"])

    def _draw_ships(self):
        scale = cfg.RENDER_WIDTH / cfg.SCREEN_WIDTH

        for nave in self.frota:
            sx = int(nave.pos[0] * scale)
            sy = int(nave.pos[1] * scale)
            if not (0 <= sx < cfg.RENDER_WIDTH and 0 <= sy < cfg.RENDER_HEIGHT):
                continue

            vx = float(nave.vel[0])
            vy = float(nave.vel[1])
            speed = math.hypot(vx, vy)
            if speed > 0.05:
                angle = math.atan2(vy, vx)
            else:
                angle = 0.0

            size = 7

            nose = (
                sx + size * math.cos(angle),
                sy + size * math.sin(angle),
            )
            left = (
                sx + size * 0.5 * math.cos(angle + 2.6),
                sy + size * 0.5 * math.sin(angle + 2.6),
            )
            right = (
                sx + size * 0.5 * math.cos(angle - 2.6),
                sy + size * 0.5 * math.sin(angle - 2.6),
            )
            rear = (
                sx + size * 0.25 * math.cos(angle + math.pi),
                sy + size * 0.25 * math.sin(angle + math.pi),
            )

            pts = [
                (int(nose[0]), int(nose[1])),
                (int(left[0]), int(left[1])),
                (int(rear[0]), int(rear[1])),
                (int(right[0]), int(right[1])),
            ]

            if nave.ativa:
                color = nave.cor
                darker = (color[0] // 2, color[1] // 2, color[2] // 2)
                pygame.draw.polygon(self.canvas, color, pts)
                pygame.draw.polygon(self.canvas, cfg.COLOR_BLACK, pts, 1)
                pygame.draw.polygon(self.canvas, darker, pts, 1)

                cockpit_x = int(sx + size * 0.3 * math.cos(angle))
                cockpit_y = int(sy + size * 0.3 * math.sin(angle))
                pygame.draw.rect(self.canvas, cfg.COLOR_WHITE,
                                 (cockpit_x - 1, cockpit_y - 1, 3, 3))
            else:
                ghost = (60, 60, 70)
                pygame.draw.polygon(self.canvas, ghost, pts)
                pygame.draw.polygon(self.canvas, cfg.COLOR_DARK_GRAY, pts, 1)

    def _draw_trails(self):
        scale = cfg.RENDER_WIDTH / cfg.SCREEN_WIDTH
        trail_spacing = 3

        for nave in self.frota:
            if not nave.ativa:
                continue
            if len(nave.trail) < 2:
                continue

            r = nave.cor[0] // 2
            g = nave.cor[1] // 2
            b = nave.cor[2] // 2
            trail_color = (r, g, b)

            for idx in range(0, len(nave.trail) - 1, trail_spacing):
                p = nave.trail[idx]
                rx = int(p[0] * scale)
                ry = int(p[1] * scale)
                if 2 <= rx < cfg.RENDER_WIDTH - 2 and 2 <= ry < cfg.RENDER_HEIGHT - 2:
                    pygame.draw.rect(self.canvas, trail_color,
                                     (rx, ry, 1, 1))

    def _draw_planets(self):
        scale = cfg.RENDER_WIDTH / cfg.SCREEN_WIDTH
        for planet in self.planets:
            px = int(planet["pos"][0] * scale)
            py = int(planet["pos"][1] * scale)
            radius = int(planet["radius"] * scale)
            color = planet["color"]

            pygame.draw.circle(self.canvas, color, (px, py), radius)
            pygame.draw.circle(self.canvas, cfg.COLOR_BLACK, (px, py), radius, 2)

    def _draw_checkpoints(self):
        scale = cfg.RENDER_WIDTH / cfg.SCREEN_WIDTH
        current_time = pygame.time.get_ticks()
        pulse = (current_time // 200) % 2

        for cp in self.checkpoints:
            cx = int(cp["pos"][0] * scale)
            cy = int(cp["pos"][1] * scale)
            size = int(cp["radius"] * scale * 0.7)

            cp_color = cfg.COLOR_YELLOW if pulse else cfg.COLOR_GOLD

            diamond = [
                (cx, cy - size),
                (cx + size, cy),
                (cx, cy + size),
                (cx - size, cy),
            ]
            pygame.draw.polygon(self.canvas, cp_color, diamond)
            pygame.draw.polygon(self.canvas, cfg.COLOR_BLACK, diamond, 1)

    def _draw_station(self):
        scale = cfg.RENDER_WIDTH / cfg.SCREEN_WIDTH
        sx = int(self.station_pos[0] * scale)
        sy = int(self.station_pos[1] * scale)
        hw = int(cfg.STATION_WIDTH * scale) // 2
        hh = int(cfg.STATION_HEIGHT * scale) // 2

        body_rect = pygame.Rect(sx - hw, sy - hh, hw * 2, hh * 2)
        pygame.draw.rect(self.canvas, cfg.COLOR_GRAY, body_rect)
        pygame.draw.rect(self.canvas, cfg.COLOR_BLACK, body_rect, 2)
        pygame.draw.rect(self.canvas, cfg.COLOR_CYAN, body_rect, 1)

    def _draw_fleet_hud(self):
        cp_max = max(n.checkpoints_coletados for n in self.frota) if self.frota else 0
        total_cp = len(self.checkpoints)

        status_color = cfg.COLOR_GREEN if self.total_alive > 0 else cfg.COLOR_RED

        lines = [
            (f"GEN {self.generation}", cfg.COLOR_CYAN),
            (f"NAVES {self.total_alive}/{self.pop_size}", status_color),
            (f"DOCAS {self.total_docked}", cfg.COLOR_GREEN if self.total_docked > 0 else cfg.COLOR_GRAY),
            (f"CP {cp_max}/{total_cp}", cfg.COLOR_YELLOW),
            (f"STEP {self.episode_steps}", cfg.COLOR_GRAY),
        ]

        x = 4
        y = 4
        for text, color in lines:
            surf = PixelFont.render(text, color)
            for ox, oy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
                shadow = PixelFont.render(text, cfg.COLOR_BLACK)
                self.canvas.blit(shadow, (x + ox, y + oy))
            self.canvas.blit(surf, (x, y))
            y += 8

    def close(self):
        if self.screen is not None:
            pygame.quit()
            self.screen = None
            self.canvas = None
            self.clock = None


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
        cls._GLYPHS['?'] = glyph(['.###.', '#...#', '....#', '...#.', '..#..', '.....', '..#..'])

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
