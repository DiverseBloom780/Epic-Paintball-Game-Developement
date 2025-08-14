import pygame, math
from core import settings as S
from core.utils import clamp
from .projectile import Paintball

class Player:
    _id_seq = 1
    def __init__(self, pos, name="Player", color=(64,160,255)):
        self.id = Player._id_seq; Player._id_seq += 1
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(0,0)
        self.name = name
        self.color = color
        self.health = S.PLAYER_MAX_HEALTH
        self.invincible = S.INVINCIBLE_SPAWN_TIME
        self.ammo = 30
        self.max_ammo = 30
        self.reload_t = 0.0
        self.fire_cd = 0.0
        self.alive = True
        self.respawn_t = 0.0

    def radius(self): return S.PLAYER_RADIUS

    def hit(self, dmg, from_id=None):
        if self.invincible > 0 or not self.alive: return
        self.health -= dmg
        if self.health <= 0:
            self.alive = False
            self.respawn_t = S.RESPAWN_TIME

    def update(self, dt, move_dir, aim_pos, shooting, reloading, solids, projectiles):
        if not self.alive:
            self.respawn_t -= dt
            if self.respawn_t <= 0:
                self.alive = True
                self.health = S.PLAYER_MAX_HEALTH
                self.invincible = S.INVINCIBLE_SPAWN_TIME
                self.pos += (10,0)  # tiny jitter to avoid spawn stack
            return

        self.invincible = max(0.0, self.invincible - dt)
        self.fire_cd = max(0.0, self.fire_cd - dt)

        # Reload
        if reloading and self.ammo < self.max_ammo and self.reload_t <= 0:
            self.reload_t = S.RELOAD_TIME
        if self.reload_t > 0:
            self.reload_t -= dt
            if self.reload_t <= 0:
                self.ammo = self.max_ammo

        # Movement
        desired = pygame.Vector2(move_dir)
        if desired.length_squared() > 0:
            desired = desired.normalize() * S.PLAYER_SPEED
        self.vel = desired
        next_pos = self.pos + self.vel * dt

        # Collide with walls (AABB circle vs rects)
        circle = pygame.Rect(next_pos.x - S.PLAYER_RADIUS, next_pos.y - S.PLAYER_RADIUS, S.PLAYER_RADIUS*2, S.PLAYER_RADIUS*2)
        blocked = False
        for w in solids:
            if circle.colliderect(w):
                blocked = True
                break
        if not blocked:
            self.pos = next_pos

        # Shooting
        if shooting and self.fire_cd <= 0 and self.ammo > 0 and self.reload_t <= 0:
            to = pygame.Vector2(aim_pos) - self.pos
            if to.length_squared() > 0:
                dirv = to.normalize()
                pb = Paintball(self.pos + dirv*S.PLAYER_RADIUS, dirv * S.PAINTBALL_SPEED, self.id, self.color)
                projectiles.append(pb)
                self.fire_cd = S.PLAYER_FIRE_COOLDOWN
                self.ammo -= 1

    def draw(self, surf):
        pygame.draw.circle(surf, self.color, self.pos, S.PLAYER_RADIUS)
        if self.invincible > 0:
            pygame.draw.circle(surf, (255,255,255,60), self.pos, S.PLAYER_RADIUS+4, 1)
