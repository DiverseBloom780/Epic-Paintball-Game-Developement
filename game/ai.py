import random, math, pygame
from core import settings as S
from core.utils import norm, length, line_of_sight, angle_deg
from .projectile import Paintball

class BotController:
    def __init__(self, player_ref, color=(220,64,64)):
        self.p = player_ref
        self.p.color = color
        self.state = "patrol"
        self.target = None
        self.fire_cd = 0.0
        self.waypoint = None
        self.repath_t = 0.0

    def update(self, dt, game):
        self.fire_cd = max(0, self.fire_cd - dt)
        if not self.p.alive: return (0, False)

        # choose target if none
        if self.target is None or not self.target.alive or self.target is self.p:
            self.target = self._pick_target(game)

        # Behavior
        move = pygame.Vector2(0,0)
        shoot = False

        if self.target:
            to = self.target.pos - self.p.pos
            dist = to.length()
            if dist < S.BOT_SIGHT_RANGE and line_of_sight(self.p.pos, self.target.pos, game.solids):
                self.state = "chase"
                move = to.normalize()
                if dist > 140:
                    move *= 1.0
                else:
                    move *= -0.6  # back up if too close
                # Shoot when roughly aimed
                if angle_deg(to, self.p.vel + pygame.Vector2(1e-3,0)) < S.BOT_FOV_DEG or dist < 220:
                    if self.fire_cd <= 0 and self.p.ammo > 0 and self.p.reload_t <= 0:
                        shoot = True
                        self.fire_cd = S.BOT_FIRE_COOLDOWN
            else:
                self.state = "patrol"
        if self.state == "patrol":
            self.repath_t -= dt
            if self.waypoint is None or self.repath_t <= 0 or (self.p.pos - self.waypoint).length() < 32:
                self.waypoint = pygame.Vector2(random.choice(game.spawn_points))
                self.repath_t = random.uniform(1.0, 2.5)
            move = (self.waypoint - self.p.pos)
            if move.length_squared() > 0:
                move = move.normalize()

        # reload occasionally
        if self.p.ammo <= 0 and self.p.reload_t <= 0:
            self.p.reload_t = 1.2

        return (move, shoot)

    def _pick_target(self, game):
        candidates = [pl for pl in game.players if pl.alive and pl is not self.p]
        return random.choice(candidates) if candidates else None
