"""
astar_planner.py — Busca A* geradora (generator com yield) com custo gravitacional.

Cada celula tem um custo extra baseado na soma do potencial gravitacional
( G * massa / distancia ) de todos os planetas. Celulas perto de planetas
massivos ficam "caras", forcando o A* a desviar para o vacuo espacial.
"""

import math
import heapq
from collections import deque
from agents.grid_map import CELL_SIZE
import config as cfg

GRAVITY_COST_FACTOR = 0.5


class AStarPlanner:

    def __init__(self, grid_map):
        self.grid = grid_map
        self.planets = getattr(grid_map, 'planets', [])

    def search(self, start_pos, goal_pos):
        sr, sc = self.grid.pos_to_cell(*start_pos)
        gr, gc = self.grid.pos_to_cell(*goal_pos)

        if not self.grid.is_passable(sr, sc):
            sr, sc = self._nearest_passable(sr, sc)
        if not self.grid.is_passable(gr, gc):
            gr, gc = self._nearest_passable(gr, gc)

        if (sr, sc) == (gr, gc):
            yield {
                "open": [],
                "closed": [],
                "current": (sr, sc),
                "path": [self.grid.cell_to_pos(sr, sc)],
            }
            return

        counter = 0
        open_heap = [(self._h(sr, sc, gr, gc), 0, counter, sr, sc)]
        g_scores = {(sr, sc): 0.0}
        came_from = {}
        closed_set = set()
        open_set = {(sr, sc)}

        while open_heap:
            f, g, _, r, c = heapq.heappop(open_heap)

            if (r, c) not in open_set:
                continue
            open_set.discard((r, c))

            yield {
                "open": list(open_set),
                "closed": list(closed_set),
                "current": (r, c),
                "path": None,
            }

            if (r, c) == (gr, gc):
                path_cells = self._reconstruct(came_from, (sr, sc), (gr, gc))
                path = [self.grid.cell_to_pos(pr, pc) for pr, pc in path_cells]
                yield {
                    "open": [],
                    "closed": list(closed_set),
                    "current": (r, c),
                    "path": path,
                }
                return

            closed_set.add((r, c))

            for nr, nc, move_cost in self._neighbors(r, c):
                if (nr, nc) in closed_set:
                    continue
                if not self.grid.is_passable(nr, nc):
                    continue

                grav_cost = self._gravity_cost(nr, nc)
                ng = g + move_cost + grav_cost
                old_g = g_scores.get((nr, nc))
                if old_g is not None and ng >= old_g:
                    continue

                came_from[(nr, nc)] = (r, c)
                g_scores[(nr, nc)] = ng
                nf = ng + self._h(nr, nc, gr, gc)
                counter += 1
                heapq.heappush(open_heap, (nf, ng, counter, nr, nc))
                open_set.add((nr, nc))

        yield {
            "open": [],
            "closed": list(closed_set),
            "current": None,
            "path": None,
        }

    def _gravity_cost(self, r, c):
        if not self.planets:
            return 0.0
        cx, cy = self.grid.cell_to_pos(r, c)
        total = 0.0
        for p in self.planets:
            px, py = float(p["pos"][0]), float(p["pos"][1])
            dist = math.hypot(cx - px, cy - py)
            if dist < 1.0:
                dist = 1.0
            total += cfg.G * p["mass"] / dist
        return total * GRAVITY_COST_FACTOR

    def _h(self, r1, c1, r2, c2):
        return math.hypot((r1 - r2) * CELL_SIZE, (c1 - c2) * CELL_SIZE)

    def _neighbors(self, r, c):
        dirs = [
            (-1, -1, 1.414), (-1, 0, 1.0), (-1, 1, 1.414),
            (0, -1, 1.0), (0, 1, 1.0),
            (1, -1, 1.414), (1, 0, 1.0), (1, 1, 1.414),
        ]
        for dr, dc, cost in dirs:
            nr, nc = r + dr, c + dc
            if self.grid._in_bounds(nr, nc):
                yield nr, nc, cost

    def _reconstruct(self, came_from, start, goal):
        path = [goal]
        curr = goal
        while curr != start:
            prev = came_from.get(curr)
            if prev is None:
                break
            path.append(prev)
            curr = prev
        path.reverse()
        return path

    def _nearest_passable(self, r, c):
        visited = {(r, c)}
        q = deque([(r, c)])
        while q:
            cr, cc = q.popleft()
            if self.grid.is_passable(cr, cc):
                return (cr, cc)
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nr, nc = cr + dr, cc + dc
                if self.grid._in_bounds(nr, nc) and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    q.append((nr, nc))
        return (r, c)
