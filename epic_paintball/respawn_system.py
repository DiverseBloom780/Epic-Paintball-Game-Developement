import time

class RespawnSystem:
    def __init__(self, respawn_time):
        self.respawn_time = respawn_time
        self.dead = {}  # player -> death_time

    def mark_dead(self, player):
        self.dead[player] = time.time()

    def update(self):
        now = time.time()
        to_respawn = []
        for p, t in list(self.dead.items()):
            if now - t >= self.respawn_time:
                to_respawn.append(p)
                del self.dead[p]
        return to_respawn
