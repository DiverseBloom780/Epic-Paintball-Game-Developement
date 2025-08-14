class ScoringSystem:
    def __init__(self):
        self.team_scores = {}

    def add_team(self, team):
        self.team_scores[team.name] = 0

    def add_point(self, team_name, pts=1):
        if team_name in self.team_scores:
            self.team_scores[team_name] += pts

    def get(self, team_name):
        return self.team_scores.get(team_name, 0)
