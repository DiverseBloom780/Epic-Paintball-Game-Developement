# paintball_gun.py
# Paintball markers (guns) with limited ammo
class PaintballGun:
    def __init__(self, ammo_capacity):
        self.ammo_capacity = ammo_capacity
        self.current_ammo = ammo_capacity

    def shoot(self):
        if self.current_ammo > 0:
            self.current_ammo -= 1
            print("Shot fired!")
        else:
            print("Out of ammo!")

    def reload(self):
        self.current_ammo = self.ammo_capacity
        print("Ammo reloaded!")

def main():
    gun = PaintballGun(10)
    gun.shoot()
    gun.reload()

if __name__ == "__main__":
    main()
