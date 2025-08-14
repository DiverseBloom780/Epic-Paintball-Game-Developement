import pygame
import random
from core.config import WIDTH, HEIGHT, OBST

def make_obstacles():
    obstacles = []
    for _ in range(8):
        w = random.randint(40, 120)
        h = random.randint(40, 120)
        x = random.randint(50, WIDTH - w - 50)
        y = random.randint(50, HEIGHT - h - 50)
        obstacles.append(pygame.Rect(x, y, w, h))
    return obstacles

def draw(surface, obstacles):
    for rect in obstacles:
        pygame.draw.rect(surface, OBST, rect)
