from enum import Enum

class GameMode(Enum):
    ELIMINATION = 1
    # CAPTURE_THE_FLAG = 2
    # KING_OF_THE_HILL = 3

class GameModes:
    def __init__(self, mode=GameMode.ELIMINATION):
        self.mode = mode

    def on_frag(self, killer_team, scoring):
        # 1 point to killer team in elimination
        scoring.add_point(killer_team, 1)
