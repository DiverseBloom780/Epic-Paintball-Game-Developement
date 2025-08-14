import pygame

class Input:
    def __init__(self):
        self.move = pygame.Vector2(0, 0)
        self.shoot = False
        self.reload = False
        self.pause = False

    def poll(self):
        self.move.update(0, 0)
        self.shoot = False
        self.reload = False
        self.pause = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]: self.move.y -= 1
        if keys[pygame.K_s]: self.move.y += 1
        if keys[pygame.K_a]: self.move.x -= 1
        if keys[pygame.K_d]: self.move.x += 1

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.pause = True
                if e.key == pygame.K_r:
                    self.reload = True
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                self.shoot = True
        return True
