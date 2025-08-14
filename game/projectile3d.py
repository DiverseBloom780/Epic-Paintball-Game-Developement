# game/projectile3d.py
class Paintball3D:
    def __init__(self, parent, origin, direction, speed=40.0, ttl=2.0, color=(0.3,0.9,0.4,1)):
        self.node = parent.attach_new_node("paintball")
        self.model = loader.loadModel("models/smiley")
        self.model.set_scale(0.12)
        self.model.set_color(*color)
        self.model.reparent_to(self.node)
        self.node.set_pos(origin)
        self.dir = direction.normalized()
        self.speed = speed
        self.ttl = ttl
        self.alive = True

    def update(self, dt):
        if not self.alive: return False
        self.ttl -= dt
        if self.ttl <= 0:
            self.node.remove_node()
            return False
        self.node.set_pos(self.node.get_pos() + self.dir * (self.speed * dt))
        return True
