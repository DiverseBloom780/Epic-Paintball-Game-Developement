import pygame
from config import WIDTH, HEIGHT, OBST

def make_obstacles():
    # A few rectangles to dodge around
    rects = [
        pygame.Rect(WIDTH*0.20, HEIGHT*0.20, 140, 30),
        pygame.Rect(WIDTH*0.55, HEIGHT*0.15, 160, 36),
        pygame.Rect(WIDTH*0.10, HEIGHT*0.60, 200, 30),
        pygame.Rect(WIDTH*0.60, HEIGHT*0.55, 220, 36),
        pygame.Rect(WIDTH*0.42, HEIGHT*0.38, 80, 150),
    ]
    return rects

def draw(surface, rects):
    for r in rects:
        pygame.draw.rect(surface, OBST, r, border_radius=6)
