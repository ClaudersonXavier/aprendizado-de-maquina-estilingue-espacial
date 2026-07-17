"""
physics.py — Funcoes puras de fisica e colisao.
Nenhuma dependencia de pygame ou estado global. Apenas matematica vetorial.
"""

import numpy as np


GRAVITY_MIN_DISTANCE = 5.0  # Distancia minima para evitar divisao por zero


def gravity_vector(ship_pos, planet_pos, planet_mass, G):
    """
    Calcula o vetor de aceleracao gravitacional exercido por um planeta sobre a nave.

    Formula: F = G * m / r^2  na direcao do centro do planeta.

    Args:
        ship_pos: np.array(2) — posicao (x, y) da nave.
        planet_pos: np.array(2) — posicao (x, y) do planeta.
        planet_mass: float — massa do planeta.
        G: float — constante gravitacional.

    Returns:
        np.array(2) — vetor de aceleracao gravitacional.
    """
    direction = planet_pos - ship_pos
    distance = float(np.linalg.norm(direction))

    if distance < GRAVITY_MIN_DISTANCE:
        distance = GRAVITY_MIN_DISTANCE

    direction_normalized = direction / distance
    magnitude = G * planet_mass / (distance ** 2)

    return direction_normalized * magnitude


def total_gravity(ship_pos, planets, G):
    """
    Soma os vetores gravitacionais de todos os planetas.

    Args:
        ship_pos: np.array(2) — posicao da nave.
        planets: list[dict] — lista de planetas com chaves 'pos', 'mass'.
        G: float — constante gravitacional.

    Returns:
        np.array(2) — aceleracao gravitacional total.
    """
    accel = np.zeros(2, dtype=np.float64)
    for planet in planets:
        planet_pos = np.array(planet["pos"], dtype=np.float64)
        accel += gravity_vector(ship_pos, planet_pos, planet["mass"], G)
    return accel


def thrust_vector(action, power):
    """
    Converte uma acao discreta em vetor de aceleracao de propulsao.

    Args:
        action: int 0-4.
            0 = nada
            1 = cima (-Y)
            2 = baixo (+Y)
            3 = esquerda (-X)
            4 = direita (+X)
        power: float — magnitude da aceleracao.

    Returns:
        np.array(2) — vetor de aceleracao.
    """
    thrust_map = {
        0: (0.0, 0.0),
        1: (0.0, -power),
        2: (0.0, power),
        3: (-power, 0.0),
        4: (power, 0.0),
    }
    return np.array(thrust_map[action], dtype=np.float64)


def apply_kinematics(pos, vel, accel, max_speed):
    """
    Aplica aceleracao, atualiza velocidade e posicao com limite de velocidade.

    Args:
        pos: np.array(2) — posicao atual.
        vel: np.array(2) — velocidade atual.
        accel: np.array(2) — aceleracao a ser aplicada.
        max_speed: float — velocidade escalar maxima.

    Returns:
        tuple[np.array(2), np.array(2)] — (nova_posicao, nova_velocidade).
    """
    vel = vel + accel
    speed = float(np.linalg.norm(vel))
    if speed > max_speed:
        vel = vel / speed * max_speed
    pos = pos + vel
    return pos, vel


def check_circle_collision(pos_a, radius_a, pos_b, radius_b):
    """
    Verifica colisao entre dois circulos.

    Args:
        pos_a: (float, float) ou np.array — centro do circulo A.
        radius_a: float — raio do circulo A.
        pos_b: (float, float) ou np.array — centro do circulo B.
        radius_b: float — raio do circulo B.

    Returns:
        bool — True se houver sobreposicao.
    """
    pa = np.asarray(pos_a, dtype=np.float64)
    pb = np.asarray(pos_b, dtype=np.float64)
    distance = float(np.linalg.norm(pa - pb))
    return distance < (radius_a + radius_b)


def check_circle_rect_collision(circle_pos, circle_radius, rect_center, rect_w, rect_h):
    """
    Verifica colisao entre um circulo e um retangulo alinhado aos eixos (AABB).

    Args:
        circle_pos: (float, float) — centro do circulo.
        circle_radius: float — raio do circulo.
        rect_center: (float, float) — centro do retangulo.
        rect_w: float — largura do retangulo.
        rect_h: float — altura do retangulo.

    Returns:
        bool — True se houver sobreposicao.
    """
    cx, cy = circle_pos
    rx, ry = rect_center
    half_w, half_h = rect_w / 2.0, rect_h / 2.0

    nearest_x = max(rx - half_w, min(cx, rx + half_w))
    nearest_y = max(ry - half_h, min(cy, ry + half_h))

    dist_x = cx - nearest_x
    dist_y = cy - nearest_y

    return (dist_x ** 2 + dist_y ** 2) < (circle_radius ** 2)


def is_out_of_bounds(pos, width, height, margin=0.0):
    """
    Verifica se uma posicao esta fora dos limites da tela.

    Args:
        pos: (float, float) — posicao a verificar.
        width: float — largura da tela.
        height: float — altura da tela.
        margin: float — tolerancia extra alem das bordas.

    Returns:
        bool — True se estiver fora.
    """
    x, y = pos
    return x < -margin or x > width + margin or y < -margin or y > height + margin
