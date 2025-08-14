import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Set up some constants
WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_SIZE = 50
PLAYER_SPEED = 5
PAINTBALL_SIZE = 10
PAINTBALL_SPEED = 10
ENEMY_SPEED = 3

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Set up the game clock
clock = pygame.time.Clock()

class Player(pygame.Rect):
    def __init__(self):
        super().__init__(WIDTH / 2, HEIGHT / 2, PLAYER_SIZE, PLAYER_SIZE)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

        # Boundary checking
        if self.x < 0:
            self.x = 0
        elif self.x > WIDTH - self.width:
            self.x = WIDTH - self.width

        if self.y < 0:
            self.y = 0
        elif self.y > HEIGHT - self.height:
            self.y = HEIGHT - self.height

class Enemy(pygame.Rect):
    def __init__(self):
        super().__init__(random.randint(0, WIDTH - PLAYER_SIZE), random.randint(0, HEIGHT - PLAYER_SIZE), PLAYER_SIZE, PLAYER_SIZE)

    def move(self, player):
        if self.x < player.x:
            self.x += ENEMY_SPEED
        elif self.x > player.x:
            self.x -= ENEMY_SPEED

        if self.y < player.y:
            self.y += ENEMY_SPEED
        elif self.y > player.y:
            self.y -= ENEMY_SPEED

class Paintball(pygame.Rect):
    def __init__(self, x, y):
        super().__init__(x, y, PAINTBALL_SIZE, PAINTBALL_SIZE)
        self.speed_x = 0
        self.speed_y = 0

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y

# Create a player instance
player = Player()
enemies = [Enemy() for _ in range(5)]
paintballs = []
enemy_paintballs = []

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            paintball = Paintball(player.centerx, player.centery)
            mouse_x, mouse_y = event.pos
            dx = mouse_x - player.centerx
            dy = mouse_y - player.centery
            dist = (dx**2 + dy**2)**0.5
            if dist != 0:
                paintball.speed_x = dx / dist * PAINTBALL_SPEED
                paintball.speed_y = dy / dist * PAINTBALL_SPEED
                paintballs.append(paintball)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player.move(0, -PLAYER_SPEED)
    if keys[pygame.K_s]:
        player.move(0, PLAYER_SPEED)
    if keys[pygame.K_a]:
        player.move(-PLAYER_SPEED, 0)
    if keys[pygame.K_d]:
        player.move(PLAYER_SPEED, 0)

    for enemy in enemies:
        enemy.move(player)
        if random.random() < 0.05:
            enemy_paintball = Paintball(enemy.centerx, enemy.centery)
            dx = player.centerx - enemy.centerx
            dy = player.centery - enemy.centery
            dist = (dx**2 + dy**2)**0.5
            if dist != 0:
                enemy_paintball.speed_x = dx / dist * PAINTBALL_SPEED
                enemy_paintball.speed_y = dy / dist * PAINTBALL_SPEED
                enemy_paintballs.append(enemy_paintball)

    for paintball in paintballs:
        paintball.move()
        if not screen.get_rect().colliderect(paintball):
            paintballs.remove(paintball)

    for enemy_paintball in enemy_paintballs:
        enemy_paintball.move()
        if not screen.get_rect().colliderect(enemy_paintball):
            enemy_paintballs.remove(enemy_paintball)

    # Draw everything
    screen.fill((255, 255, 255))  # Fill the screen with white
    pygame.draw.rect(screen, (0, 0, 255), player)  # Draw the player
    for enemy in enemies:
        pygame.draw.rect(screen, (255, 0, 0), enemy)  # Draw the enemy
    for paintball in paintballs:
        pygame.draw.ellipse(screen, (0, 255, 0), paintball)  # Draw the paintball
    for enemy_paintball in enemy_paintballs:
        pygame.draw.ellipse(screen, (255, 255, 0), enemy_paintball)  # Draw the enemy paintball

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(FPS)
