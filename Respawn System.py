# respawn_system.py
# Adds a Respawn System
class RespawnSystem:
    def __init__(self, respawn_time):
        self.respawn_time = respawn_time
        self.players = {}

    def add_player(self, player):
        self.players[player] = None

    def player_died(self, player):
        self.players[player] = time.time()

    def update(self):
        current_time = time.time()
        for player, death_time in self.players.items():
            if death_time is not None and current_time - death_time >= self.respawn_time:
                self.players[player] = None
                print(f"Player {player} has respawned!")

import time

def main():
    respawn_system = RespawnSystem(5)
    respawn_system.add_player("Player 1")
    respawn_system.player_died("Player 1")
    while True:
        respawn_system.update()
        time.sleep(1)

if __name__ == "__main__":
    main()
