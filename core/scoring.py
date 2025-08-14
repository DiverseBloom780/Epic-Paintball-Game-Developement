# core/scoring.py
class ScoringSystem:
    def __init__(self):
        self.scores = {}

    def add_team(self, team):
        self.scores[team.name] = 0

    def add(self, team_name, points=1):
        if team_name in self.scores:
            self.scores[team_name] += points

    def get(self, team_name):
        return self.scores.get(team_name, 0)
