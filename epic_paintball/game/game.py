import pygame, sys, json, random, time
from core import settings as S
from core.input import Input
from .assets import load_assets
from .map import TileMap
from .player import Player
from .projectile import Paintball
from .ai import BotController
from . import ui

class Game:
    def __init__(self, screen, map_data, player_color=(64,160,255), bot_count=3, ai_enabled=True):
        self.screen = screen
        self.assets = load_assets()
        self.map = TileMap(map_data)
        self.solids = self.map.walls
        self.spawn_points = self.map.spawn_points
        self.players = []
        self.projectiles = []
        self.bots = []  # (Player, BotController)
        self.round_time = 120.0
        self._spawn_player("You", color=player_color)
        if ai_enabled:
            for i in range(bot_count):
                self._spawn_bot(f"Bot{i+1}")
        self.clock = pygame.time.Clock()
        self.input = Input()

    def _spawn_player(self, name, color=(64,160,255)):
        p = Player(random.choice(self.spawn_points), name, color=color)
        self.players.append(p)
        self.local_player = p

    def _spawn_bot(self, name):
        p = Player(random.choice(self.spawn_points), name, color=(220,64,64))
        bot = BotController(p, color=(220,64,64))
        self.players.append(p)
        self.bots.append(bot)

    def _aim_pos(self):
        return pygame.Vector2(pygame.mouse.get_pos())

    def _damage_at(self, pos, owner_id):
        for pl in self.players:
            if not pl.alive or pl.id == owner_id: continue
            if (pl.pos - pos).length() <= (pl.radius()+8):
                pl.hit(35, owner_id)

    def update(self, dt):
        # input
        if not self.input.poll():
            return False

        # bots AI -> produce move/shoot
        bot_moves = {}
        for bot in self.bots:
            mv, shoot = bot.update(dt, self)
            bot_moves[bot.p.id] = (mv, shoot)

        # update players
        for pl in self.players:
            if pl is self.local_player:
                mv = self.input.move
                shoot = self.input.shoot
                reload = self.input.reload
            else:
                mv, shoot = bot_moves.get(pl.id, (pygame.Vector2(0,0), False))
                reload = False
            pl.update(dt, mv, self._aim_pos(), shoot, reload, self.solids, self.projectiles)

        # projectiles
        alive_proj = []
        for pb in self.projectiles:
            alive = pb.update(dt, self.solids)
            if not alive:
                # splash damage where it ends
                self._damage_at(pb.pos, pb.owner_id)
            else:
                alive_proj.append(pb)
        self.projectiles = alive_proj

        # timer
        self.round_time -= dt
        return True

    def draw(self):
        # world
        self.map.draw(self.screen, self.assets["tile"])
        # projectiles
        for pb in self.projectiles:
            pb.draw(self.screen)
        # players
        for pl in self.players:
            pl.draw(self.screen)
        # hud
        ui.draw_hud(self.screen, self.local_player, max(0, self.round_time))

    def run(self):
        running = True
        while running and self.round_time > 0:
            dt = self.clock.tick(S.FPS) / 1000.0
            running = self.update(dt)
            self.draw()
            pygame.display.flip()
