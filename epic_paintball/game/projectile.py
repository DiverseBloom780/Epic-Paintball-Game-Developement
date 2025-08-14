import pygame, math
from core import settings as S

class Paintball:
    __slots__ = ("pos","vel","owner_id","time","color")
    def __init__(self, pos, vel, owner_id, color=(255,255,255)):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(vel)
        self.owner_id = owner_id
        self.time = 0.0
        self.color = color

    def update(self, dt, solids):
        self.pos += self.vel * dt
        self.time += dt
        # collide with walls
        rect = pygame.Rect(self.pos.x-3, self.pos.y-3, 6, 6)
        for w in solids:
            if rect.colliderect(w):
                return False
        return self.time < S.PAINTBALL_LIFETIME

    def draw(self, surf):
        pygame.draw.circle(surf, self.color, self.pos, S.PAINTBALL_RADIUS)
