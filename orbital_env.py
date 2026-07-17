"""
orbital_env.py — Ambiente Odisséia Orbital.
Simulador 2D de navegacao espacial com gravidade, checkpoints e estacao.
Interface padrao: reset(), step(action), render(), close().
"""

import math
import numpy as np
import pygame

import config as cfg
import physics as phys


class OrbitalEnv:
    """
    Ambiente de navegacao orbital 2D.

    A nave deve partir do planeta de lancamento, navegar por um campo
    gravitacional com 6 planetas, coletar checkpoints de combustivel e
    atracar na estacao espacial.

    Atributos:
        action_space_n (int): 5 acoes discretas (0-4).
        obs_shape (tuple): (7,) — dimensao do vetor de observacao.
    """

    def __init__(self, render_mode=None):
        self.render_mode = render_mode

        # Interface descritiva (nao depende de gymnasium)
        self.action_space_n = 5
        self.obs_shape = (7,)

        # Planetas (copia do config para evitar mutacao compartilhada)
        self.planets = [
            {
                "pos": np.array(p["pos"], dtype=np.float64),
                "radius": p["radius"],
                "mass": p["mass"],
                "color": p["color"],
            }
            for p in cfg.PLANETS
        ]

        # Checkpoints
        self.checkpoints = []
        for cp in cfg.CHECKPOINTS:
            self.checkpoints.append({
                "pos": np.array(cp["pos"], dtype=np.float64),
                "radius": cp["radius"],
                "collected": False,
            })

        # Estacao espacial
        self.station_pos = np.array(cfg.STATION_POS, dtype=np.float64)
        self.station_radius = cfg.STATION_RADIUS

        # Estado da nave (inicializado no reset)
        self.ship_pos = None
        self.ship_vel = None
        self.fuel = 0.0
        self.done = False
        self.episode_reward = 0.0
        self.episode_steps = 0
        self.last_info = {"status": "not_started"}

        # Rastro orbital
        self.trail = []

        # Pygame (lazy init no primeiro render)
        self.screen = None
        self.clock = None
        self._font = None
        self._small_font = None

        if render_mode is not None:
            self._init_pygame()

    # ================================================================
    # Metodos da Interface Padrao
    # ================================================================

    def reset(self):
        """
        Reinicia o episodio. Restaura posicao, velocidade, combustivel,
        checkpoints e rastro. Retorna a observacao inicial.

        Returns:
            np.ndarray: vetor de observacao com 7 elementos.
        """
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

        return self._get_state()

    def step(self, action):
        """
        Executa um passo da simulacao.

        Ordem das operacoes:
        1. Consome combustivel se acao != 0.
        2. Calcula aceleracao (gravidade + propulsao).
        3. Atualiza cinematica (velocidade e posicao).
        4. Verifica colisoes (planetas, bordas, checkpoints, estacao).
        5. Verifica combustivel zerado.
        6. Aplica recompensas continuas.

        Args:
            action (int): 0=nada, 1=cima, 2=baixo, 3=esquerda, 4=direita.

        Returns:
            tuple: (observation, reward, done, info)
        """
        if self.done:
            return self._get_state(), 0.0, True, self.last_info

        reward = 0.0
        info = {"status": "alive", "checkpoint_collected": False}

        # --- 1. Consumo de combustivel ---
        thrust_available = False
        if action != 0 and self.fuel >= cfg.FUEL_COST_PER_THRUST:
            self.fuel -= cfg.FUEL_COST_PER_THRUST
            thrust_available = True

        # --- 2. Calculo da aceleracao ---
        grav_accel = phys.total_gravity(self.ship_pos, self.planets, cfg.G)

        if thrust_available:
            thrust_accel = phys.thrust_vector(action, cfg.THRUST_POWER)
        else:
            thrust_accel = np.zeros(2, dtype=np.float64)

        total_accel = grav_accel + thrust_accel

        # --- 3. Atualizacao cinematica ---
        self.ship_pos, self.ship_vel = phys.apply_kinematics(
            self.ship_pos, self.ship_vel, total_accel, cfg.MAX_SPEED
        )

        # --- 4. Atualiza rastro ---
        self.trail.append(tuple(self.ship_pos))
        if len(self.trail) > cfg.MAX_TRAIL_LENGTH:
            self.trail.pop(0)

        # --- 5. Verifica colisao com planetas ---
        for planet in self.planets:
            if phys.check_circle_collision(
                self.ship_pos, cfg.SHIP_RADIUS,
                planet["pos"], planet["radius"],
            ):
                reward = cfg.REWARD_FAILURE
                self.done = True
                info["status"] = "crashed_planet"
                info["planet_mass"] = planet["mass"]
                self.last_info = info
                self.episode_reward += reward
                return self._get_state(), reward, True, info

        # --- 6. Verifica saida dos limites da tela ---
        if phys.is_out_of_bounds(
            self.ship_pos, cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT
        ):
            reward = cfg.REWARD_FAILURE
            self.done = True
            info["status"] = "out_of_bounds"
            self.last_info = info
            self.episode_reward += reward
            return self._get_state(), reward, True, info

        # --- 7. Verifica colisao com checkpoints ---
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

        # --- 8. Verifica colisao com a estacao ---
        station_center = (
            float(self.station_pos[0]),
            float(self.station_pos[1]),
        )
        if phys.check_circle_rect_collision(
            self.ship_pos, cfg.SHIP_RADIUS,
            station_center, cfg.STATION_WIDTH, cfg.STATION_HEIGHT,
        ):
            reward += cfg.REWARD_SUCCESS
            self.done = True
            info["status"] = "docked"
            self.last_info = info
            self.episode_reward += reward
            return self._get_state(), reward, True, info

        # --- 9. Verifica combustivel zerado ---
        if self.fuel <= 0.0:
            reward = cfg.REWARD_FAILURE
            self.done = True
            info["status"] = "no_fuel"
            self.last_info = info
            self.episode_reward += reward
            return self._get_state(), reward, True, info

        # --- 10. Recompensas continuas ---
        reward += cfg.REWARD_STEP
        if action != 0:
            reward += cfg.REWARD_THRUST_COST

        self.episode_reward += reward
        self.episode_steps += 1
        self.last_info = info

        return self._get_state(), reward, self.done, info

    # ================================================================
    # Observacao
    # ================================================================

    def _get_state(self):
        """
        Constroi o vetor de observacao com 7 elementos normalizados.

        Returns:
            np.ndarray: [pos_x, pos_y, vel_x, vel_y, fuel, dist_checkpoint, dist_station]
        """
        # Distancia ao primeiro checkpoint nao coletado
        checkpoint_dist = 0.0
        for cp in self.checkpoints:
            if not cp["collected"]:
                checkpoint_dist = float(np.linalg.norm(self.ship_pos - cp["pos"]))
                break

        station_dist = float(np.linalg.norm(self.ship_pos - self.station_pos))

        return np.array([
            float(self.ship_pos[0]),
            float(self.ship_pos[1]),
            float(self.ship_vel[0]),
            float(self.ship_vel[1]),
            float(self.fuel),
            checkpoint_dist,
            station_dist,
        ], dtype=np.float64)

    # ================================================================
    # Renderizacao
    # ================================================================

    def render(self):
        """Renderiza o estado atual do ambiente na janela pygame."""
        if self.screen is None:
            self._init_pygame()

        self.screen.fill(cfg.COLOR_BG)

        self._draw_trail()
        self._draw_planets()
        self._draw_checkpoints()
        self._draw_station()
        self._draw_ship()
        self._draw_launch_indicator()
        self._draw_hud()

        if self.done:
            self._draw_status_overlay()

        pygame.display.flip()
        self.clock.tick(cfg.FPS)

    def close(self):
        """Fecha a janela pygame e libera recursos."""
        if self.screen is not None:
            pygame.quit()
            self.screen = None
            self.clock = None
            self._font = None
            self._small_font = None

    # ================================================================
    # Inicializacao do Pygame
    # ================================================================

    def _init_pygame(self):
        """Inicializa pygame e cria a janela (chamado sob demanda)."""
        if self.screen is not None:
            return
        pygame.init()
        self.screen = pygame.display.set_mode(
            (cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT)
        )
        pygame.display.set_caption("Odisseia Orbital")
        self.clock = pygame.time.Clock()
        self._font = pygame.font.Font(None, 28)
        self._small_font = pygame.font.Font(None, 18)

    # ================================================================
    # Desenho dos Elementos
    # ================================================================

    def _draw_trail(self):
        """Desenha o rastro orbital (trilha) conectando os ultimos pontos."""
        if len(self.trail) < 2:
            return

        total = len(self.trail)
        for i in range(total - 1):
            p1 = self.trail[i]
            p2 = self.trail[i + 1]

            # Degrade do inicio (transparente) ao fim (opaco)
            progress = i / max(total - 1, 1)
            intensity = int(50 + progress * 180)
            base = cfg.COLOR_TRAIL
            r = min(255, base[0] + intensity // 6)
            g = min(255, base[1] + intensity // 6)
            b = min(255, base[2] + intensity // 6)

            pygame.draw.line(self.screen, (r, g, b), p1, p2, width=2)

    def _draw_planets(self):
        """Desenha todos os planetas com gradiente e borda."""
        for planet in self.planets:
            px = int(planet["pos"][0])
            py = int(planet["pos"][1])
            radius = planet["radius"]

            # Corpo principal
            pygame.draw.circle(
                self.screen, planet["color"], (px, py), radius,
            )

            # Borda escura para profundidade
            border_color = tuple(max(0, c - 40) for c in planet["color"])
            pygame.draw.circle(
                self.screen, border_color, (px, py), radius, width=2,
            )

            # Brilho no canto superior-esquerdo (efeito de iluminacao)
            highlight_radius = max(4, radius // 3)
            highlight_x = px - radius // 3
            highlight_y = py - radius // 3
            lighter = tuple(min(255, c + 80) for c in planet["color"])
            pygame.draw.circle(
                self.screen, lighter,
                (highlight_x, highlight_y),
                highlight_radius,
            )

    def _draw_checkpoints(self):
        """Desenha checkpoints nao coletados com efeito pulsante."""
        current_time = pygame.time.get_ticks()
        for cp in self.checkpoints:
            if cp["collected"]:
                continue

            cx = int(cp["pos"][0])
            cy = int(cp["pos"][1])
            radius = cp["radius"]

            # Efeito pulsante via senoide
            pulse = (math.sin(current_time * 0.004) + 1.0) * 0.5
            color = self._lerp_color(
                cfg.COLOR_CHECKPOINT_GLOW, cfg.COLOR_CHECKPOINT, pulse
            )

            # Nucleo
            pygame.draw.circle(self.screen, color, (cx, cy), radius)

            # Aureola externa
            aura_radius = radius + 4 + int(pulse * 3)
            aura_color = (color[0], color[1], color[2], 50)
            aura_surf = pygame.Surface(
                (aura_radius * 2, aura_radius * 2), pygame.SRCALPHA
            )
            pygame.draw.circle(
                aura_surf, aura_color,
                (aura_radius, aura_radius), aura_radius,
            )
            self.screen.blit(aura_surf, (cx - aura_radius, cy - aura_radius))

            # Cruz interna (icone de cristal/coleta)
            inner = max(3, radius // 3)
            offset = max(2, radius // 4)
            pygame.draw.line(
                self.screen, cfg.COLOR_BG,
                (cx - inner, cy), (cx + inner, cy), width=1,
            )
            pygame.draw.line(
                self.screen, cfg.COLOR_BG,
                (cx, cy - inner), (cx, cy + inner), width=1,
            )

    def _draw_station(self):
        """Desenha a estacao espacial como um retangulo com detalhes."""
        sx = int(self.station_pos[0])
        sy = int(self.station_pos[1])
        hw = cfg.STATION_WIDTH // 2
        hh = cfg.STATION_HEIGHT // 2

        rect = pygame.Rect(sx - hw, sy - hh, cfg.STATION_WIDTH, cfg.STATION_HEIGHT)

        # Corpo da estacao
        pygame.draw.rect(self.screen, cfg.COLOR_STATION, rect)
        pygame.draw.rect(self.screen, cfg.COLOR_STATION_BORDER, rect, width=2)

        # Painéis solares (detalhes visuais)
        panel_w, panel_h = 8, 14
        # Painel esquerdo
        pygame.draw.rect(
            self.screen, (52, 73, 94),
            (sx - hw - panel_w - 4, sy - panel_h // 2, panel_w, panel_h),
        )
        # Painel direito
        pygame.draw.rect(
            self.screen, (52, 73, 94),
            (sx + hw + 4, sy - panel_h // 2, panel_w, panel_h),
        )

        # Luz de atracagem (piscante)
        dock_light_on = (pygame.time.get_ticks() % 1000) < 600
        dock_color = (46, 204, 113) if dock_light_on else (39, 174, 96)
        pygame.draw.circle(self.screen, dock_color, (sx, sy), 4)

    def _draw_ship(self):
        """
        Desenha a nave como um triangulo orientado na direcao da velocidade.
        Se a velocidade for quase nula, a nave aponta para a direita.
        """
        x, y = float(self.ship_pos[0]), float(self.ship_pos[1])
        vx, vy = float(self.ship_vel[0]), float(self.ship_vel[1])

        speed = math.hypot(vx, vy)
        if speed > 0.05:
            angle = math.atan2(vy, vx)
        else:
            angle = 0.0

        size = 10
        nose = (
            x + size * math.cos(angle),
            y + size * math.sin(angle),
        )
        left_wing = (
            x + size * 0.5 * math.cos(angle + 2.6),
            y + size * 0.5 * math.sin(angle + 2.6),
        )
        right_wing = (
            x + size * 0.5 * math.cos(angle - 2.6),
            y + size * 0.5 * math.sin(angle - 2.6),
        )

        pygame.draw.polygon(
            self.screen, cfg.COLOR_SHIP,
            [nose, left_wing, right_wing],
        )
        pygame.draw.polygon(
            self.screen, cfg.COLOR_SHIP_OUTLINE,
            [nose, left_wing, right_wing], width=1,
        )

        # Pequeno circulo no centro da nave
        pygame.draw.circle(self.screen, cfg.COLOR_BG, (int(x), int(y)), 2)

    def _draw_launch_indicator(self):
        """Desenha uma seta indicando o planeta de lancamento."""
        px = int(self.planets[0]["pos"][0]) + self.planets[0]["radius"] + 8
        py = int(self.planets[0]["pos"][1])
        label = self._small_font.render("LANCAMENTO", True, cfg.COLOR_HUD_TEXT)
        label_rect = label.get_rect(midleft=(px, py - self.planets[0]["radius"] - 6))
        self.screen.blit(label, label_rect)

    # ================================================================
    # HUD
    # ================================================================

    def _draw_hud(self):
        """Desenha o HUD: barra de combustivel, recompensa, passos, checkpoints."""
        if self._font is None:
            return

        margin_x, margin_y = 15, 15
        bar_w, bar_h = 200, 16

        # --- Barra de combustivel ---
        pygame.draw.rect(
            self.screen, cfg.COLOR_FUEL_BAR_BG,
            (margin_x, margin_y, bar_w, bar_h),
        )

        fuel_ratio = self.fuel / cfg.MAX_FUEL
        if fuel_ratio > 0:
            fuel_width = int(bar_w * fuel_ratio)
            if fuel_ratio > 0.5:
                fuel_color = cfg.COLOR_FUEL_BAR
            elif fuel_ratio > 0.25:
                fuel_color = cfg.COLOR_FUEL_BAR_MID
            else:
                fuel_color = cfg.COLOR_FUEL_BAR_LOW
            pygame.draw.rect(
                self.screen, fuel_color,
                (margin_x, margin_y, fuel_width, bar_h),
            )

        pygame.draw.rect(
            self.screen, cfg.COLOR_HUD_TEXT,
            (margin_x, margin_y, bar_w, bar_h), width=1,
        )

        # --- Textos do HUD ---
        fuel_text = self._small_font.render(
            f"Combustivel: {int(self.fuel)} / {int(cfg.MAX_FUEL)}",
            True, cfg.COLOR_HUD_TEXT,
        )
        self.screen.blit(fuel_text, (margin_x, margin_y + bar_h + 4))

        reward_text = self._small_font.render(
            f"Recompensa: {self.episode_reward:+.1f}",
            True, cfg.COLOR_HUD_TEXT,
        )
        self.screen.blit(reward_text, (margin_x, margin_y + bar_h + 22))

        steps_text = self._small_font.render(
            f"Passos: {self.episode_steps}",
            True, cfg.COLOR_HUD_TEXT,
        )
        self.screen.blit(steps_text, (margin_x, margin_y + bar_h + 40))

        collected = sum(1 for cp in self.checkpoints if cp["collected"])
        total_cp = len(self.checkpoints)
        cp_text = self._small_font.render(
            f"Checkpoints: {collected} / {total_cp}",
            True, cfg.COLOR_HUD_TEXT,
        )
        self.screen.blit(cp_text, (margin_x, margin_y + bar_h + 58))

    # ================================================================
    # Overlay de Status
    # ================================================================

    def _draw_status_overlay(self):
        """Exibe overlay translucido com o resultado do episodio."""
        status = self.last_info.get("status", "unknown")

        messages = {
            "docked": ("SUCESSO! Estacao alcancada!", cfg.COLOR_SUCCESS),
            "crashed_planet": ("FRACASSO! Colisao com planeta!", cfg.COLOR_FAILURE),
            "out_of_bounds": ("FRACASSO! Fora dos limites da tela!", cfg.COLOR_FAILURE),
            "no_fuel": ("FRACASSO! Combustivel esgotado!", cfg.COLOR_FAILURE),
        }
        msg, color = messages.get(status, ("Fim do Episodio", cfg.COLOR_HUD_TEXT))

        # Fundo semi-transparente
        overlay = pygame.Surface(
            (cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))

        # Mensagem principal
        text = self._font.render(msg, True, color)
        text_rect = text.get_rect(
            center=(cfg.SCREEN_WIDTH // 2, cfg.SCREEN_HEIGHT // 2 - 20)
        )
        self.screen.blit(text, text_rect)

        # Estatisticas finais
        stats = self._small_font.render(
            f"Recompensa final: {self.episode_reward:+.1f}     "
            f"Passos: {self.episode_steps}     "
            f"Checkpoints: {sum(1 for cp in self.checkpoints if cp['collected'])}/{len(self.checkpoints)}",
            True, cfg.COLOR_HUD_TEXT,
        )
        stats_rect = stats.get_rect(
            center=(cfg.SCREEN_WIDTH // 2, cfg.SCREEN_HEIGHT // 2 + 20)
        )
        self.screen.blit(stats, stats_rect)

        # Instrucao
        hint = self._small_font.render(
            "Pressione [R] para reiniciar  |  [ESC] para sair",
            True, (180, 180, 180),
        )
        hint_rect = hint.get_rect(
            center=(cfg.SCREEN_WIDTH // 2, cfg.SCREEN_HEIGHT // 2 + 50)
        )
        self.screen.blit(hint, hint_rect)

    # ================================================================
    # Metodos Auxiliares
    # ================================================================

    @staticmethod
    def _point_visible(point):
        """Verifica se um ponto esta dentro da area visivel da tela."""
        x, y = point
        return 0 <= x <= cfg.SCREEN_WIDTH and 0 <= y <= cfg.SCREEN_HEIGHT

    @staticmethod
    def _lerp_color(c1, c2, t):
        """Interpola linearmente entre duas cores RGB."""
        return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
