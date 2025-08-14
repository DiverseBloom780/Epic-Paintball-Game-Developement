# teams.py
#Creates Team-Based GamePlay
class Team:
    def __init__(self, name):
        self.name = name
        self.players = []

    def add_player(self, player):
        self.players.append(player)

    def remove_player(self, player):
        self.players.remove(player)

class Player:
    def __init__(self, name):
        self.name = name
        self.team = None

    def join_team(self, team):
        self.team = team
        team.add_player(self)

def main():
    team1 = Team("Red Team")
    team2 = Team("Blue Team")

    player1 = Player("Player 1")
    player1.join_team(team1)

    print(team1.players[0].name)

if __name__ == "__main__":
    main()
