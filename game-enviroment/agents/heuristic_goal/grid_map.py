"""
grid_map.py — Discretizacao do espaco continuo em grid 40x30.

A margem de seguranca agora e proporcional a massa do planeta:
  - Planetas massivos (ex: gigante gasoso) tem margem maior
  - Planetas pequenos tem margem menor
  - global_margin_boost: incrementado a cada colisao, forcando rotas mais conservadoras
"""

import math
import numpy as np
import config as cfg

CELL_SIZE = 20
GRID_COLS = cfg.SCREEN_WIDTH // CELL_SIZE
GRID_ROWS = cfg.SCREEN_HEIGHT // CELL_SIZE

BASE_SAFETY = 10
MASS_SCALE = 0.8


def _safety_for_planet(mass):
    return BASE_SAFETY + MASS_SCALE * math.sqrt(mass)


class GridMap:

    def __init__(self, planets, checkpoints=None, station_pos=None,
                 global_margin_boost=0.0):
        self.planets = list(planets)
        self.global_margin_boost = global_margin_boost
        self.grid = np.zeros((GRID_ROWS, GRID_COLS), dtype=bool)
        self._build()
        if checkpoints is not None:
            self._unblock_checkpoints(checkpoints)
        if station_pos is not None:
            self._unblock_cell(*station_pos)

    def _build(self):
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                cx, cy = self.cell_to_pos(r, c)
                for p in self.planets:
                    px, py = float(p["pos"][0]), float(p["pos"][1])
                    margin = _safety_for_planet(p["mass"]) + self.global_margin_boost
                    if math.hypot(cx - px, cy - py) < p["radius"] + margin:
                        self.grid[r, c] = True
                        break

    def increase_margins(self, delta=5.0):
        self.global_margin_boost += delta
        self.grid = np.zeros((GRID_ROWS, GRID_COLS), dtype=bool)
        self._build()

    def _unblock_checkpoints(self, checkpoints):
        for cp in checkpoints:
            if not cp.get("collected", False):
                self._unblock_cell(
                    float(cp["pos"][0]), float(cp["pos"][1])
                )
            else:
                r, c = self.pos_to_cell(
                    float(cp["pos"][0]), float(cp["pos"][1])
                )
                if self._in_bounds(r, c):
                    self.grid[r, c] = True

    def _unblock_cell(self, x, y):
        r, c = self.pos_to_cell(x, y)
        if self._in_bounds(r, c):
            self.grid[r, c] = False
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                nr, nc = r + dr, c + dc
                if self._in_bounds(nr, nc):
                    self.grid[nr, nc] = False

    def pos_to_cell(self, x, y):
        c = int(x / CELL_SIZE)
        r = int(y / CELL_SIZE)
        return (max(0, min(r, GRID_ROWS - 1)), max(0, min(c, GRID_COLS - 1)))

    def cell_to_pos(self, r, c):
        x = c * CELL_SIZE + CELL_SIZE / 2.0
        y = r * CELL_SIZE + CELL_SIZE / 2.0
        return (x, y)

    def is_passable(self, r, c):
        if not self._in_bounds(r, c):
            return False
        return not self.grid[r, c]

    def _in_bounds(self, r, c):
        return 0 <= r < GRID_ROWS and 0 <= c < GRID_COLS
