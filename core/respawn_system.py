# core/respawn_system.py
import time

class RespawnSystem:
    def __init__(self, respawn_time):
        self.respawn_time = respawn_time
        self.dead = {}  # entity -> time_of_death

    def mark_dead(self, entity):
        self.dead[entity] = time.time()

    def update(self):
        now = time.time()
        ready = []
        for ent, t in list(self.dead.items()):
            if now - t >= self.respawn_time:
                ready.append(ent)
                del self.dead[ent]
        return ready
