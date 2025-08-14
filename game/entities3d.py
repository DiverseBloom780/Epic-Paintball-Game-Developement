# game/entities3d.py
from panda3d.core import NodePath
from core.config import PLAYER_MAX_HP, AMMO_CAPACITY, RELOAD_TIME

class Player3D:
    def __init__(self, name, color, team_name, base):
        self.base = base
        self.name = name
        self.team_name = team_name
        self.hp = PLAYER_MAX_HP
        self.alive = True
        self.invuln = 0.0
        self.node = base.render.attach_new_node(f"player-{name}")
        # Use small model but hide it (pure first-person)
        model = base.loader.loadModel("models/smiley")
        model.set_scale(0.2); model.reparent_to(self.node); model.hide()
        # Gun mechanics
        self.capacity = AMMO_CAPACITY
        self.ammo = self.capacity
        self.reload_t = 0.0
        self.reload_time = RELOAD_TIME

    def start_reload(self):
        if self.ammo < self.capacity and self.reload_t <= 0:
            self.reload_t = self.reload_time

    def can_fire(self):
        return self.alive and self.ammo > 0 and self.reload_t <= 0

    def consume_shot(self):
        if self.ammo > 0:
            self.ammo -= 1

    def take_hit(self, dmg):
        if not self.alive: return False
        self.hp -= dmg
        if self.hp <= 0:
            self.alive = False
        return not self.alive

    def update(self, dt):
        if self.reload_t > 0:
            self.reload_t -= dt
            if self.reload_t <= 0:
                self.ammo = self.capacity
                self.reload_t = 0.0

class Enemy3D:
    def __init__(self, name, color, team_name, base, pos=(0,0,2.0)):
        self.base = base
        self.name = name
        self.team_name = team_name
        self.hp = 100
        self.alive = True
        self.invuln = 0.0
        self.node = base.render.attach_new_node(f"enemy-{name}")
        model = base.loader.loadModel("models/frowney")
        model.set_scale(0.6)
        # Color tint is optional; these models have built-in colors
        model.reparent_to(self.node)
        self.node.set_pos(*pos)
        self.speed = 6.0

    def take_hit(self, dmg):
        if not self.alive: return False
        self.hp -= dmg
        if self.hp <= 0:
            self.alive = False
            self.node.set_z(-100)  # hide below ground
        return not self.alive

    def update(self, dt, target_pos):
        if not self.alive: return
        vec = target_pos - self.node.get_pos()
        vec.z = 0
        dist = vec.length()
        if dist > 0.01:
            vec.normalize()
            move = vec * self.speed * dt
            self.node.set_pos(self.node.get_pos() + move)
