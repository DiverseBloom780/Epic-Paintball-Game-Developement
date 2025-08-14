# game/team.py
class Team:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.players = []

    def add_player(self, player):
        self.players.append(player)

    def remove_player(self, player):
        if player in self.players:
            self.players.remove(player)
