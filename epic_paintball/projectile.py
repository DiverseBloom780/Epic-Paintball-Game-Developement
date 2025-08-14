import pygame, math
from config import PAINTBALL_RADIUS, PAINTBALL_SPEED

class Paintball:
    __slots__ = ("pos","vel","owner","team_name","alive","life","color")
    def __init__(self, pos, direction, owner, team_name, color, speed=PAINTBALL_SPEED):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(direction) * speed
        self.owner = owner
        self.team_name = team_name
        self.color = color
        self.alive = True
        self.life = 1.2  # seconds

    def update(self, dt, bounds, obstacles):
        if not self.alive: return
        self.pos += self.vel * dt
        self.life -= dt
        if self.life <= 0: 
            self.alive = False
            return
        # bounds
        if not bounds.collidepoint(self.pos.x, self.pos.y):
            self.alive = False
            return
        # obstacle hit
        r = pygame.Rect(self.pos.x-PAINTBALL_RADIUS, self.pos.y-PAINTBALL_RADIUS, PAINTBALL_RADIUS*2, PAINTBALL_RADIUS*2)
        for ob in obstacles:
            if r.colliderect(ob):
                self.alive = False
                return

    def draw(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.pos.x), int(self.pos.y)), PAINTBALL_RADIUS)
