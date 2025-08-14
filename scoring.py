# scoring.py

class ScoringSystem:
    def __init__(self):
        self.score = 0

    def increment_score(self):
        self.score += 1

    def get_score(self):
        return self.score

def main():
    scoring_system = ScoringSystem()
    scoring_system.increment_score()
    print(scoring_system.get_score())

if __name__ == "__main__":
    main()
