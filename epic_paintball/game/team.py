class Team:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.players = []
        self.score = 0

    def add_player(self, p):
        self.players.append(p)

    def remove_player(self, p):
        if p in self.players:
            self.players.remove(p)
