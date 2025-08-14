import pygame, math
from core.config import BLUE, FIRE_COOLDOWN, HEIGHT, PLAYER_MAX_HP, PLAYER_SIZE, PLAYER_SPEED, RED, RED
from game.gun import PaintballGun
from core.config import WIDTH
from game.projectile import Paintball

class Player:
    def __init__(self, x, y, name, color, team_name):
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.name = name
        self.color = color
        self.team_name = team_name
        self.hp = PLAYER_MAX_HP
        self.alive = True
        self.invuln = 0.6
        self.fire_cd = 0.0
        self.gun = PaintballGun()

    def center(self):
        return (self.rect.centerx, self.rect.centery)

    def move(self, mv, dt, obstacles):
        if not self.alive: return
        dx, dy = mv
        dx *= PLAYER_SPEED * dt
        dy *= PLAYER_SPEED * dt

        # Horizontal
        self.rect.x += int(dx)
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > WIDTH: self.rect.right = WIDTH
        for ob in obstacles:
            if self.rect.colliderect(ob):
                if dx > 0: self.rect.right = ob.left
                elif dx < 0: self.rect.left = ob.right

        # Vertical
        self.rect.y += int(dy)
        if self.rect.top < 0: self.rect.top = 0
        if self.rect.bottom > HEIGHT: self.rect.bottom = HEIGHT
        for ob in obstacles:
            if self.rect.colliderect(ob):
                if dy > 0: self.rect.bottom = ob.top
                elif dy < 0: self.rect.top = ob.bottom

    def update(self, dt):
        self.fire_cd = max(0.0, self.fire_cd - dt)
        if self.invuln > 0: self.invuln -= dt
        self.gun.update(dt)

    def try_shoot(self, aim_pos):
        if not self.alive: return None
        if self.fire_cd > 0: return None
        if not self.gun.try_fire(): return None
        ax, ay = aim_pos
        cx, cy = self.center()
        vx, vy = ax - cx, ay - cy
        l = max(1e-6, (vx*vx+vy*vy) ** 0.5)
        dirv = (vx/l, vy/l)
        self.fire_cd = FIRE_COOLDOWN
        return Paintball((cx, cy), dirv, self, self.team_name, self.color)

    def take_hit(self, dmg):
        if not self.alive or self.invuln > 0: return False
        self.hp -= dmg
        if self.hp <= 0:
            self.alive = False
            return True
        return False

    def draw(self, surf):
        pygame.draw.rect(surf, self.color, self.rect, border_radius=6)
        # HP bar
        pct = max(0, self.hp) / PLAYER_MAX_HP
        if pct < 1:
            pygame.draw.rect(surf, (40,40,44), (self.rect.x, self.rect.y-8, self.rect.w, 6), border_radius=3)
            pygame.draw.rect(surf, (90,230,140), (self.rect.x, self.rect.y-8, int(self.rect.w*pct), 6), border_radius=3)
