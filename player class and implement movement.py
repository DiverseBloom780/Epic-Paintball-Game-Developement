import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up some constants
WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_SIZE = 50
PLAYER_SPEED = 5

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

# Create a player instance
player = Player()

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player.move(0, -PLAYER_SPEED)
    if keys[pygame.K_s]:
        player.move(0, PLAYER_SPEED)
    if keys[pygame.K_a]:
        player.move(-PLAYER_SPEED, 0)
    if keys[pygame.K_d]:
        player.move(PLAYER_SPEED, 0)

    # Draw everything
    screen.fill((255, 255, 255))  # Fill the screen with white
    pygame.draw.rect(screen, (0, 0, 255), player)  # Draw the player

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(FPS)
