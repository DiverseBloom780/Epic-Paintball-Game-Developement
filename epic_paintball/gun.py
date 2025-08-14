from config import AMMO_CAPACITY, RELOAD_TIME

class PaintballGun:
    def __init__(self):
        self.capacity = AMMO_CAPACITY
        self.ammo = self.capacity
        self.reload_t = 0.0  # > 0 while reloading

    def try_fire(self):
        if self.reload_t > 0: 
            return False
        if self.ammo > 0:
            self.ammo -= 1
            return True
        return False

    def start_reload(self):
        if self.ammo < self.capacity and self.reload_t <= 0:
            self.reload_t = RELOAD_TIME

    def update(self, dt):
        if self.reload_t > 0:
            self.reload_t -= dt
            if self.reload_t <= 0:
                self.ammo = self.capacity
