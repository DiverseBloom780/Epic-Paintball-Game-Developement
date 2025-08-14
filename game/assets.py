import pygame, os
from core import settings as S
from core.config import PAINTBALL_RADIUS

def load_placeholder_circle(radius, color):
    surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
    pygame.draw.circle(surf, color, (radius, radius), radius)
    return surf

def load_assets():
    # Procedural placeholders
    player_blue = load_placeholder_circle(S.PLAYER_RADIUS, (64,160,255))
    player_red = load_placeholder_circle(S.PLAYER_RADIUS, (220,64,64))
    paintball = load_placeholder_circle(S.PAINTBALL_RADIUS, (255, 255, 255))

    # Wall tile
    tile = pygame.Surface((S.TILE_SIZE, S.TILE_SIZE))
    tile.fill((60, 60, 70))
    for i in range(0, S.TILE_SIZE, 6):
        tile.set_at((i, i%S.TILE_SIZE), (80, 80, 95))

    return {
        "player_blue": player_blue,
        "player_red": player_red,
        "paintball": paintball,
        "tile": tile,
    }