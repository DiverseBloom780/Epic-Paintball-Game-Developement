# game/game_modes.py
from enum import Enum

class GameMode(Enum):
    ELIMINATION = 1
    CAPTURE_THE_FLAG = 2

class GameModes:
    def __init__(self, mode=GameMode.ELIMINATION):
        self.mode = mode

    def on_frag(self, team_name, scoring):
        scoring.add(team_name, 1)
