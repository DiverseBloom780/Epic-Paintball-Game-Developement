# field_obstacles.py
# Adds Field Obstacles
class FieldObstacle:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Bunker(FieldObstacle):
    def __init__(self, x, y):
        super().__init__(x, y)

class Wall(FieldObstacle):
    def __init__(self, x, y):
        super().__init__(x, y)

def main():
    bunker = Bunker(10, 20)
    wall = Wall(30, 40)
    print(bunker.x, bunker.y)
    print(wall.x, wall.y)

if __name__ == "__main__":
    main()
