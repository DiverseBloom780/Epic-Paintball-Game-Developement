# main.py
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import WindowProperties, Vec3, CardMaker, AmbientLight, DirectionalLight, TextNode
import sys, time, random, math

from core.config import WIDTH, HEIGHT, FPS, PLAYER_SPEED, PLAYER_MAX_HP, AMMO_CAPACITY, RELOAD_TIME, RESPAWN_TIME, BLUE, RED
from core.scoring import ScoringSystem
from core.respawn_system import RespawnSystem
from core.team_communication import TeamCommunication
from game.team import Team
from game.game_modes import GameModes, GameMode
from game.entities3d import Player3D, Enemy3D
from game.projectile3d import Paintball3D

WORLD_SIZE = 80.0  # half-extent of square arena

class EpicPaintball3D(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.disableMouse()

        # Window & mouse
        props = WindowProperties()
        props.setSize(WIDTH, HEIGHT)
        props.setCursorHidden(True)
        props.setMouseMode(WindowProperties.M_relative)
        self.win.requestProperties(props)

        # Systems
        self.scoring = ScoringSystem()
        self.respawns = RespawnSystem(RESPAWN_TIME)
        self.comms = TeamCommunication()
        self.modes = GameModes(GameMode.ELIMINATION)

        # Teams
        self.team_blue = Team("Blue", BLUE)
        self.team_red  = Team("Red", RED)
        self.scoring.add_team(self.team_blue)
        self.scoring.add_team(self.team_red)

        # Scene
        self._build_arena()
        self._setup_lights()

        # Player
        self.player = Player3D("You", BLUE, self.team_blue.name, base=self)
        self.player.node.set_pos(0, 0, 2.0)
        self.team_blue.add_player(self.player)

        # Camera
        self.camera.reparentTo(self.player.node)
        self.camera.set_pos(0, 0, 1.7)
        self.heading = 0.0
        self.pitch = 0.0
        self.mouse_sens = 0.12

        # Enemies
        self.enemies = []
        for i in range(6):
            ex = random.uniform(-WORLD_SIZE*0.6, WORLD_SIZE*0.6)
            ey = random.uniform(-WORLD_SIZE*0.6, WORLD_SIZE*0.6)
            bot = Enemy3D(f"Bot{i+1}", RED, self.team_red.name, base=self, pos=(ex, ey, 2.0))
            self.team_red.add_player(bot)
            self.enemies.append(bot)

        # Projectiles
        self.projectiles = []

        # Input
        self.keys = {"w":False, "s":False, "a":False, "d":False}
        self.accept("escape", sys.exit)
        for k in "wsad":
            self.accept(k, self._set_key, [k, True])
            self.accept(f"{k}-up", self._set_key, [k, False])
        self.accept("mouse1", self._on_shoot)
        self.accept("r", self._on_reload)

        # Crosshair
        self._build_crosshair()

        # HUD
        self.hud = self._make_text_node("", (0.02, 0.94))

        # Loop
        self.last_time = time.time()
        self.taskMgr.add(self._update, "update")

    # ---------- Scene ----------
    def _build_arena(self):
        cm = CardMaker("ground")
        cm.set_frame(-WORLD_SIZE, WORLD_SIZE, -WORLD_SIZE, WORLD_SIZE)
        ground = self.render.attach_new_node(cm.generate())
        ground.set_hpr(0, -90, 0)
        ground.set_pos(0, 0, 0)
        ground.set_color(0.15, 0.17, 0.2, 1)

        # perimeter walls
        def wall(a, b):
            cmw = CardMaker("wall")
            length = (Vec3(b[0]-a[0], b[1]-a[1], 0)).length()
            cmw.set_frame(0, length, 0, 4.0)
            w = self.render.attach_new_node(cmw.generate())
            w.look_at(b[0], b[1], 0)
            w.set_pos(a[0], a[1], 0)
            w.set_two_sided(True)
            w.set_color(0.35, 0.37, 0.42, 1)
            return w
        s = WORLD_SIZE
        wall((-s,-s),( s,-s))
        wall(( s,-s),( s, s))
        wall(( s, s),(-s, s))
        wall((-s, s),(-s,-s))

    def _setup_lights(self):
        amb = AmbientLight("amb"); amb.set_color((0.6,0.6,0.7,1))
        amb_np = self.render.attach_new_node(amb)
        self.render.set_light(amb_np)
        d = DirectionalLight("dir"); d.set_color((0.7,0.7,0.8,1))
        d_np = self.render.attach_new_node(d); d_np.set_hpr(-40, -45, 0)
        self.render.set_light(d_np)

    def _build_crosshair(self):
        cm = CardMaker("cross")
        size = 0.01
        v = self.aspect2d.attach_new_node(cm.generate())
        v.set_scale(size, 1, size*4); v.set_pos(0, 0, 0); v.set_color(1,1,1,1)
        h = self.aspect2d.attach_new_node(cm.generate())
        h.set_scale(size*4, 1, size); h.set_pos(0, 0, 0); h.set_color(1,1,1,1)

    def _make_text_node(self, text, pos_norm):
        tn = TextNode('hud'); tn.set_text(text); tn.set_text_color(1,1,1,1); tn.set_align(TextNode.ALeft)
        np = self.aspect2d.attach_new_node(tn)
        np.set_scale(0.05)
        np.set_pos(pos_norm[0]*2-1, 0, pos_norm[1]*2-1)
        return tn

    # ---------- Input ----------
    def _set_key(self, k, v): self.keys[k] = v
    def _on_reload(self): self.player.start_reload()
    def _on_shoot(self):
        if self.player.can_fire():
            self.player.consume_shot()
            origin = self.camera.get_pos(self.render)
            fwd = self.camera.get_quat(self.render).get_forward()
            proj = Paintball3D(self.render, origin, fwd, speed=40.0, ttl=2.0, color=(0.3,0.9,0.4,1))
            self.projectiles.append(proj)

    # ---------- Update ----------
    def _update(self, task: Task):
        now = time.time()
        dt = now - self.last_time
        self.last_time = now

        # Mouse look
        if self.mouseWatcherNode.hasMouse():
            m = self.mouseWatcherNode.getMouse()  # (-1..1)
            self.heading -= m.getX() * 80.0 * self.mouse_sens
            self.pitch   -= m.getY() * 80.0 * self.mouse_sens
            self.pitch = max(-89, min(89, self.pitch))
            self.camera.set_hpr(self.heading, self.pitch, 0)
            self.win.movePointer(0, int(self.win.getXSize()/2), int(self.win.getYSize()/2))

        # Movement
        move = Vec3(0,0,0)
        if self.keys["w"]: move.y += 1
        if self.keys["s"]: move.y -= 1
        if self.keys["a"]: move.x -= 1
        if self.keys["d"]: move.x += 1
        if move.length() > 0:
            move.normalize()
            move *= (PLAYER_SPEED/60.0) * (dt*FPS)
            self.player.node.set_pos(self.player.node, move)

        # Arena clamp
        pos = self.player.node.get_pos()
        pos.x = max(-WORLD_SIZE+1.0, min(WORLD_SIZE-1.0, pos.x))
        pos.y = max(-WORLD_SIZE+1.0, min(WORLD_SIZE-1.0, pos.y))
        self.player.node.set_pos(pos)

        # Update player
        self.player.update(dt)

        # Enemies simple chase
        for bot in self.enemies:
            if not bot.alive: continue
            bot.update(dt, target_pos=self.player.node.get_pos())

        # Projectiles
        alive = []
        for p in self.projectiles:
            if p.update(dt):
                # enemy hit check
                for bot in self.enemies:
                    if bot.alive and (bot.node.get_pos() - p.node.get_pos()).length() < 1.0:
                        if bot.take_hit(50):
                            self.comms.send("System", f"You splatted {bot.name}")
                            self.modes.on_frag(self.player.team_name, self.scoring)
                        p.alive = False
                        p.node.remove_node()
                        break
                if p.alive: alive.append(p)
        self.projectiles = alive

        # Respawns
        for who in self.respawns.update():
            if isinstance(who, Player3D):
                who.alive = True; who.hp = PLAYER_MAX_HP
                who.node.set_pos(0,0,2.0)
            elif isinstance(who, Enemy3D):
                who.alive = True; who.hp = 100
                who.node.set_pos(random.uniform(-10,10), random.uniform(-10,10), 2.0)

        # HUD
        ammo_txt = "RELOADING..." if self.player.reload_t > 0 else f"Ammo: {self.player.ammo}/{self.player.capacity}"
        self.hud.setText(f"Blue: {self.scoring.get('Blue')}  Red: {self.scoring.get('Red')}    HP: {max(0,self.player.hp)}    {ammo_txt}")

        return Task.cont

if __name__ == "__main__":
    app = EpicPaintball3D()
    app.run()
