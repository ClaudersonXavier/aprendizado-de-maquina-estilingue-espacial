"""
auto_pilot.py — Piloto com velocidade-alvo e economia de combustivel.

Em vez de Bang-Bang puro (que acelera todo frame), o piloto agora:
  1. Define uma velocidade-alvo baseada na distancia ate o waypoint
  2. Se ja esta rapido o suficiente na direcao certa → COAST (acao 0)
  3. So aciona propulsor para corrigir velocidade ou desvio
  4. So entra em EVASAO se estiver a < 20px da superficie (emergencia real)
"""

import math
import config as cfg


class AutoPilot:

    def __init__(self, path, planets):
        self.waypoints = list(path)
        self.planets = list(planets)
        self.tolerance = 15.0

    def get_action(self, obs):
        x, y = obs[0], obs[1]
        vx, vy = obs[2], obs[3]
        fuel = obs[4]

        nearest_planet, surface_dist = self._nearest_surface_dist(x, y)

        if surface_dist < 20 and fuel >= cfg.FUEL_COST_PER_THRUST:
            return self._evade(x, y, nearest_planet)

        self._advance_waypoints(x, y)

        if not self.waypoints:
            return 0

        if fuel < cfg.FUEL_COST_PER_THRUST:
            return 0

        wx, wy = self.waypoints[0]
        dx = wx - x
        dy = wy - y
        dist = math.hypot(dx, dy)

        if dist < 0.01:
            return 0

        speed = math.hypot(vx, vy)
        vel_toward = (vx * dx + vy * dy) / dist

        gx, gy = self._gravity_at(x, y)
        grav_toward = (gx * dx + gy * dy) / dist

        need_thrust = False

        if vel_toward < 0.3:
            need_thrust = True
        elif grav_toward < -0.08 and speed > 0.3:
            need_thrust = True
        elif vel_toward < 0.8 and dist > 120:
            need_thrust = True

        if not need_thrust:
            return 0

        if abs(dx) > abs(dy):
            return 4 if dx > 0 else 3
        else:
            return 1 if dy < 0 else 2

    def _evade(self, x, y, planet):
        px, py = float(planet["pos"][0]), float(planet["pos"][1])
        dx = x - px
        dy = y - py
        if abs(dx) > abs(dy):
            return 4 if dx > 0 else 3
        else:
            return 1 if dy < 0 else 2

    def _advance_waypoints(self, x, y):
        while self.waypoints:
            wx, wy = self.waypoints[0]
            dist = math.hypot(x - wx, y - wy)
            if dist < self.tolerance:
                self.waypoints.pop(0)
            elif len(self.waypoints) >= 2:
                nx, ny = self.waypoints[1]
                if math.hypot(x - nx, y - ny) < dist:
                    self.waypoints.pop(0)
                else:
                    break
            else:
                break

    def _gravity_at(self, x, y):
        gx, gy = 0.0, 0.0
        for p in self.planets:
            px, py = float(p["pos"][0]), float(p["pos"][1])
            dx = px - x
            dy = py - y
            dist = math.hypot(dx, dy)
            if dist < 5.0:
                dist = 5.0
            mag = cfg.G * p["mass"] / (dist * dist)
            gx += (dx / dist) * mag
            gy += (dy / dist) * mag
        return gx, gy

    def _nearest_surface_dist(self, x, y):
        best_dist = float('inf')
        best = None
        for p in self.planets:
            px, py = float(p["pos"][0]), float(p["pos"][1])
            dist = math.hypot(x - px, y - py) - p["radius"]
            if dist < best_dist:
                best_dist = dist
                best = p
        return best, best_dist

    def has_path(self):
        return len(self.waypoints) > 0

    def distance_to_next(self, x, y):
        if not self.waypoints:
            return 0.0
        wx, wy = self.waypoints[0]
        return math.hypot(x - wx, y - wy)
