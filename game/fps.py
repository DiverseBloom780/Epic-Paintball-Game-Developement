import math
import pygame
from core.config import WIDTH, HEIGHT, BG, WHITE, FPS

# Raycasting parameters
FOV = math.radians(70)     # field of view
NUM_RAYS = 240             # number of vertical slices
MAX_DEPTH = 1000           # max ray distance (pixels)
WALL_SIZE = 64             # world tile size in pixels
STEP = 4                   # ray march step in pixels

# Weapon sway/bob
BOB_AMPLITUDE = 6
BOB_FREQ = 8.0

def grid_at(game_map, x, y):
    """Return cell value at pixel coords (x,y). 0 empty, 1 wall."""
    if x < 0 or y < 0:
        return 1
    gx = int(x // WALL_SIZE)
    gy = int(y // WALL_SIZE)
    if gy < 0 or gy >= len(game_map) or gx < 0 or gx >= len(game_map[0]):
        return 1
    return game_map[gy][gx]

def cast_single_ray(px, py, angle, game_map):
    """Return (distance, hit) using DDA-like raymarching."""
    dist = 0.0
    dx = math.cos(angle)
    dy = math.sin(angle)
    x, y = px, py
    while dist < MAX_DEPTH:
        x += dx * STEP
        y += dy * STEP
        dist += STEP
        if grid_at(game_map, x, y) == 1:
            return dist, True
    return MAX_DEPTH, False

def render_first_person(screen, px, py, angle, game_map, t, gun_img=None):
    """Render sky/ground, wall slices, crosshair, and weapon overlay."""
    screen.fill(BG)
    half_h = HEIGHT // 2

    # Sky / ground
    pygame.draw.rect(screen, (62, 78, 112), (0, 0, WIDTH, half_h))
    pygame.draw.rect(screen, (35, 38, 42), (0, half_h, WIDTH, half_h))

    start_angle = angle - FOV / 2
    ray_step = FOV / NUM_RAYS
    col_w = WIDTH / NUM_RAYS

    for r in range(NUM_RAYS):
        ray_ang = start_angle + r * ray_step
        dist, hit = cast_single_ray(px, py, ray_ang, game_map)
        if not hit:
            continue
        # Fisheye correction
        dist *= math.cos(angle - ray_ang)

        # Wall slice height
        slice_h = max(8, int((WALL_SIZE * 420) / (dist + 0.001)))
        shade = max(30, min(225, int(255 - (dist * 0.18))))
        color = (shade, shade, shade)

        x = int(r * col_w)
        y = half_h - slice_h // 2
        pygame.draw.rect(screen, color, (x, y, int(col_w) + 1, slice_h))

    draw_crosshair(screen)
    draw_weapon(screen, t, gun_img)

def draw_crosshair(screen):
    cx, cy = WIDTH // 2, HEIGHT // 2
    gap = 6
    arm = 12
    thick = 2
    # horizontal
    pygame.draw.rect(screen, WHITE, (cx - gap - arm, cy - thick//2, arm, thick))
    pygame.draw.rect(screen, WHITE, (cx + gap,       cy - thick//2, arm, thick))
    # vertical
    pygame.draw.rect(screen, WHITE, (cx - thick//2, cy - gap - arm, thick, arm))
    pygame.draw.rect(screen, WHITE, (cx - thick//2, cy + gap,       thick, arm))

def draw_weapon(screen, t, gun_img):
    if gun_img is None:
        # Simple placeholder weapon
        w, h = 280, 140
        base_x = WIDTH//2 - w//2
        base_y = HEIGHT - h - 10
        bob = int(BOB_AMPLITUDE * math.sin(t * BOB_FREQ))
        r = pygame.Rect(base_x, base_y + bob, w, h)
        pygame.draw.rect(screen, (50, 50, 55), r, border_radius=16)
        pygame.draw.rect(screen, (80, 80, 90), r.inflate(-20, -60), border_radius=12)
    else:
        bob = int(BOB_AMPLITUDE * math.sin(t * BOB_FREQ))
        pos = (WIDTH//2 - gun_img.get_width()//2, HEIGHT - gun_img.get_height() + bob)
        screen.blit(gun_img, pos)

def hitscan(px, py, angle, max_range, game_map):
    """Raycast for shooting; return (hit, x, y, distance)."""
    dist = 0.0
    dx = math.cos(angle)
    dy = math.sin(angle)
    x, y = px, py
    while dist < max_range:
        x += dx * STEP
        y += dy * STEP
        dist += STEP
        if grid_at(game_map, x, y) == 1:
            return True, x, y, dist
    return False, x, y, dist
