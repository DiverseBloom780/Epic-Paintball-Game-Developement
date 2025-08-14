import json, pygame
from core import settings as S

class TileMap:
    def __init__(self, map_json):
        self.walls = []
        self.width = 0
        self.height = 0
        self.spawn_points = []
        self._load(map_json)

    def _load(self, mp):
        self.width = mp.get("width", 20)
        self.height = mp.get("height", 12)
        tiles = mp["tiles"]
        self.spawn_points = [pygame.Vector2(p) for p in mp.get("spawns", [(80,80),(600,400),(1000,600)])]
        for y, row in enumerate(tiles):
            for x, cell in enumerate(row):
                if cell == 1:  # wall
                    r = pygame.Rect(x*S.TILE_SIZE, y*S.TILE_SIZE, S.TILE_SIZE, S.TILE_SIZE)
                    self.walls.append(r)

    def draw(self, surf, tile_surf):
        # Fill background
        surf.fill((24, 26, 30))
        # Draw walls
        for r in self.walls:
            surf.blit(tile_surf, r.topleft)
