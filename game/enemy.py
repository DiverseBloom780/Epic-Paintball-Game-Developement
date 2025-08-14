import pygame, random, math
from game.player import Player
from core.config import ENEMY_ACCURACY_NOISE, ENEMY_COOLDOWN, ENEMY_SIZE, ENEMY_SPEED, RED, RED
from game.projectile import Paintball
from game.gun import PaintballGun

class Enemy:
    def __init__(self, x, y, name, color, team_name):
        self.rect = pygame.Rect(x, y, ENEMY_SIZE, ENEMY_SIZE)
        self.name = name
        self.color = color
        self.team_name = team_name
        self.alive = True
        self.hp = 100
        self.fire_cd = 0.0
        self.gun = PaintballGun()
        self.invuln = 0.6

    def center(self):
        return (self.rect.centerx, self.rect.centery)

    def update(self, dt, player_pos, obstacles):
        self.fire_cd = max(0, self.fire_cd - dt)
        if self.invuln > 0: self.invuln -= dt
        self.gun.update(dt)
        # simple chase toward player with obstacle avoidance by sliding
        px, py = player_pos
        cx, cy = self.center()
        dx, dy = px - cx, py - cy
        l = max(1e-6, (dx*dx+dy*dy)**0.5)
        mvx, mvy = dx/l, dy/l

        # move step-by-step (basic AABB resolving)
        step = ENEMY_SPEED * dt
        # horizontal
        self.rect.x += int(mvx*step)
        for ob in obstacles:
            if self.rect.colliderect(ob):
                if mvx > 0: self.rect.right = ob.left
                else: self.rect.left = ob.right
        # vertical
        self.rect.y += int(mvy*step)
        for ob in obstacles:
            if self.rect.colliderect(ob):
                if mvy > 0: self.rect.bottom = ob.top
                else: self.rect.top = ob.bottom

        # shoot occasionally when roughly aligned
        dist = ((px-cx)**2 + (py-cy)**2) ** 0.5
        if dist < 500 and self.fire_cd <= 0 and self.gun.ammo > 0 and self.gun.reload_t <= 0:
            aimx, aimy = px, py
            # add some inaccuracy
            ang = math.atan2(aimy-cy, aimx-cx) + random.uniform(-ENEMY_ACCURACY_NOISE, ENEMY_ACCURACY_NOISE)
            dirv = (math.cos(ang), math.sin(ang))
            self.fire_cd = ENEMY_COOLDOWN
            self.gun.ammo -= 1
            return Paintball((cx, cy), dirv, self, self.team_name, self.color)
        if self.gun.ammo <= 0:
            self.gun.start_reload()
        return None

    def take_hit(self, dmg):
        if not self.alive or self.invuln > 0: return False
        self.hp -= dmg
        if self.hp <= 0:
            self.alive = False
            return True
        return False

    def draw(self, surf):
        pygame.draw.rect(surf, self.color, self.rect, border_radius=6)
