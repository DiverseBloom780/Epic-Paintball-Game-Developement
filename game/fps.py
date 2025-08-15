import math
import pygame
from typing import Iterable, List, Optional, Sequence, Tuple

from core.config import WIDTH, HEIGHT, BG, WHITE, FPS

# --------------------------------------------------------------------------------------
# Core params (kept)
# --------------------------------------------------------------------------------------
FOV = math.radians(70)     # field of view
NUM_RAYS = 240             # number of vertical slices
MAX_DEPTH = 1000           # max ray distance (pixels)
WALL_SIZE = 64             # world tile size in pixels
STEP = 4                   # ray march step in pixels

# Weapon sway/bob (kept)
BOB_AMPLITUDE = 6
BOB_FREQ = 8.0

# --------------------------------------------------------------------------------------
# New visual tuning / helpers
# --------------------------------------------------------------------------------------
FOG_COLOR = (35, 38, 42)   # matches ground; used to fade distant walls
FOG_DENSITY = 0.0025       # exponential fog density (higher = thicker fog)
VIGNETTE_ALPHA = 80        # subtle darkening at edges; 0 disables

EPS = 1e-9


# --------------------------------------------------------------------------------------
# Map helpers (kept)
# --------------------------------------------------------------------------------------
def grid_at(game_map: Sequence[Sequence[int]], x: float, y: float) -> int:
    """Return cell value at pixel coords (x,y). 0 empty, 1 wall."""
    if x < 0 or y < 0:
        return 1
    gx = int(x // WALL_SIZE)
    gy = int(y // WALL_SIZE)
    if gy < 0 or gy >= len(game_map) or gx < 0 or gx >= len(game_map[0]):
        return 1
    return game_map[gy][gx]


# --------------------------------------------------------------------------------------
# Ray casting
# --------------------------------------------------------------------------------------
def cast_single_ray(px: float, py: float, angle: float, game_map: Sequence[Sequence[int]]) -> Tuple[float, bool]:
    """
    Return (distance_px, hit) using improved DDA grid stepping for precision.
    Kept original signature; internally delegates to DDA for fewer artifacts.
    """
    dist, hit, *_ = cast_single_ray_dda(px, py, angle, game_map, MAX_DEPTH)
    return dist, hit


def cast_single_ray_dda(
    px: float,
    py: float,
    angle: float,
    game_map: Sequence[Sequence[int]],
    max_depth: float = MAX_DEPTH
) -> Tuple[float, bool, int, float, float, float, int]:
    """
    NEW: Robust DDA ray cast in grid space.
    Returns: (dist_px, hit, side, tex_u, hit_x, hit_y, cell_value)
      - side: 0 hit vertical grid line, 1 hit horizontal
      - tex_u: [0..1] fractional coord along the wall (for texturing)
      - hit_x/y: impact point in pixels
      - cell_value: the map value that was hit
    """
    # Convert to grid units (tile = 1)
    pos_x = px / WALL_SIZE
    pos_y = py / WALL_SIZE

    map_w = len(game_map[0])
    map_h = len(game_map)

    ray_dx = math.cos(angle)
    ray_dy = math.sin(angle)

    # DDA precompute
    delta_x = float("inf") if abs(ray_dx) < EPS else abs(1.0 / ray_dx)
    delta_y = float("inf") if abs(ray_dy) < EPS else abs(1.0 / ray_dy)

    map_x = int(math.floor(pos_x))
    map_y = int(math.floor(pos_y))

    if ray_dx < 0:
        step_x = -1
        side_x = (pos_x - map_x) * delta_x
    else:
        step_x = 1
        side_x = (map_x + 1.0 - pos_x) * delta_x

    if ray_dy < 0:
        step_y = -1
        side_y = (pos_y - map_y) * delta_y
    else:
        step_y = 1
        side_y = (map_y + 1.0 - pos_y) * delta_y

    side = 0  # 0: X, 1: Y
    hit = False
    cell_value = 0

    # Ray march in grid space with safe bounds
    max_steps = (map_w + map_h) * 4 + 1
    steps = 0

    while steps < max_steps:
        steps += 1
        if side_x < side_y:
            side_x += delta_x
            map_x += step_x
            side = 0
        else:
            side_y += delta_y
            map_y += step_y
            side = 1

        if map_x < 0 or map_x >= map_w or map_y < 0 or map_y >= map_h:
            break

        cell_value = game_map[map_y][map_x]
        if cell_value != 0:
            hit = True
            break

    if not hit:
        # Missed within bounds; clamp to max depth
        hit_x = px + ray_dx * max_depth
        hit_y = py + ray_dy * max_depth
        return max_depth, False, side, 0.0, hit_x, hit_y, 0

    # Perpendicular distance to wall in grid units
    if side == 0:
        # vertical wall
        perp = (map_x - pos_x + (1 - step_x) * 0.5) / (ray_dx if abs(ray_dx) > EPS else EPS)
    else:
        # horizontal wall
        perp = (map_y - pos_y + (1 - step_y) * 0.5) / (ray_dy if abs(ray_dy) > EPS else EPS)

    perp = max(0.0, perp)
    dist_px = perp * WALL_SIZE
    dist_px = min(dist_px, max_depth)

    # Impact position (pixels)
    hit_x = px + ray_dx * dist_px
    hit_y = py + ray_dy * dist_px

    # Fractional coord along the hit wall for potential texturing
    if side == 0:
        wall_x = pos_y + perp * ray_dy
    else:
        wall_x = pos_x + perp * ray_dx
    tex_u = wall_x - math.floor(wall_x)

    return dist_px, True, side, tex_u, hit_x, hit_y, cell_value


def build_depth_map(
    px: float,
    py: float,
    angle: float,
    game_map: Sequence[Sequence[int]],
    *,
    num_rays: int = NUM_RAYS,
    fov: float = FOV,
    max_depth: float = MAX_DEPTH
) -> List[Tuple[float, bool, int, float]]:
    """
    NEW: Casts a fan of rays and returns a compact depth buffer per ray:
    [(distance_px, hit, side, tex_u), ...] length == num_rays
    """
    start_angle = angle - fov / 2
    step = fov / num_rays
    out: List[Tuple[float, bool, int, float]] = []

    # Use DDA for all rays (perp distances—no extra fish-eye correction needed)
    for r in range(num_rays):
        ray_ang = start_angle + r * step
        dist, hit, side, tex_u, *_ = cast_single_ray_dda(px, py, ray_ang, game_map, max_depth)
        out.append((dist, hit, side, tex_u))
    return out


# --------------------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------------------
def render_first_person(
    screen: pygame.Surface,
    px: float,
    py: float,
    angle: float,
    game_map: Sequence[Sequence[int]],
    t: float,
    gun_img: Optional[pygame.Surface] = None,
    *,
    sprites: Optional[Iterable["Sprite"]] = None,
    fog_color: Tuple[int, int, int] = FOG_COLOR,
    fog_density: float = FOG_DENSITY,
    show_minimap: bool = False,
) -> None:
    """Render sky/ground, wall slices, crosshair, (optional) sprites and weapon."""
    screen.fill(BG)
    half_h = HEIGHT // 2

    # Sky / ground
    pygame.draw.rect(screen, (62, 78, 112), (0, 0, WIDTH, half_h))
    pygame.draw.rect(screen, (35, 38, 42), (0, half_h, WIDTH, half_h))

    # Depth buffer (perp distances, already fish-eye safe)
    depth = build_depth_map(px, py, angle, game_map, num_rays=NUM_RAYS, fov=FOV, max_depth=MAX_DEPTH)

    col_w = WIDTH / NUM_RAYS

    # Walls
    for r, (dist, hit, side, tex_u) in enumerate(depth):
        if not hit:
            continue

        # Wall slice height (standard perspective scale)
        slice_h = max(8, int((WALL_SIZE * 420) / (dist + 0.001)))

        # Base grey, with slight darkening on "side" hits for simple lighting
        shade = max(30, min(230, int(255 - (dist * 0.18))))
        if side == 1:
            shade = int(shade * 0.85)

        # Apply exponential fog
        fog = math.exp(-fog_density * dist)
        color = (
            int(shade * fog + fog_color[0] * (1 - fog)),
            int(shade * fog + fog_color[1] * (1 - fog)),
            int(shade * fog + fog_color[2] * (1 - fog)),
        )

        x = int(r * col_w)
        y = half_h - slice_h // 2
        pygame.draw.rect(screen, color, (x, y, int(col_w) + 1, slice_h))

    # Sprites (billboards) with occlusion
    if sprites:
        render_sprites(screen, px, py, angle, sprites, depth, fov=FOV)

    # Crosshair & weapon
    draw_crosshair(screen)  # kept API (now supports optional spread)
    draw_weapon(screen, t, gun_img)

    # Optional vignette for atmosphere
    if VIGNETTE_ALPHA > 0:
        draw_vignette(screen, VIGNETTE_ALPHA)

    # Optional mini-map overlay (top-left)
    if show_minimap:
        render_minimap(screen, game_map, px, py, angle, rays=depth, sprites=sprites)


def draw_crosshair(screen: pygame.Surface, spread: int = 0) -> None:
    """Kept function; now supports optional spread (px) for feedback."""
    cx, cy = WIDTH // 2, HEIGHT // 2
    gap = 6 + spread
    arm = 12 + spread // 2
    thick = 2
    # horizontal
    pygame.draw.rect(screen, WHITE, (cx - gap - arm, cy - thick // 2, arm, thick))
    pygame.draw.rect(screen, WHITE, (cx + gap, cy - thick // 2, arm, thick))
    # vertical
    pygame.draw.rect(screen, WHITE, (cx - thick // 2, cy - gap - arm, thick, arm))
    pygame.draw.rect(screen, WHITE, (cx - thick // 2, cy + gap, thick, arm))


def draw_weapon(screen: pygame.Surface, t: float, gun_img: Optional[pygame.Surface]) -> None:
    """Kept function; slight bobbing retained."""
    if gun_img is None:
        # Simple placeholder weapon
        w, h = 280, 140
        base_x = WIDTH // 2 - w // 2
        base_y = HEIGHT - h - 10
        bob = int(BOB_AMPLITUDE * math.sin(t * BOB_FREQ))
        r = pygame.Rect(base_x, base_y + bob, w, h)
        pygame.draw.rect(screen, (50, 50, 55), r, border_radius=16)
        pygame.draw.rect(screen, (80, 80, 90), r.inflate(-20, -60), border_radius=12)
    else:
        bob = int(BOB_AMPLITUDE * math.sin(t * BOB_FREQ))
        pos = (WIDTH // 2 - gun_img.get_width() // 2, HEIGHT - gun_img.get_height() + bob)
        screen.blit(gun_img, pos)


def hitscan(px: float, py: float, angle: float, max_range: float, game_map: Sequence[Sequence[int]]) -> Tuple[bool, float, float, float]:
    """
    Raycast for shooting; return (hit, x, y, distance).
    Upgraded to use DDA for accurate impact points.
    """
    dist, hit, *_rest = cast_single_ray_dda(px, py, angle, game_map, max_range)
    if hit:
        # reconstruct hit point from returned tuple to avoid drift
        _, _, _, _, hx, hy, _ = cast_single_ray_dda(px, py, angle, game_map, max_range)
        return True, hx, hy, dist
    # Fall back if no hit within range
    hx = px + math.cos(angle) * max_range
    hy = py + math.sin(angle) * max_range
    return False, hx, hy, max_range


# --------------------------------------------------------------------------------------
# New: Billboards (sprite) rendering with depth occlusion
# --------------------------------------------------------------------------------------
class Sprite:
    """Simple world-space billboard."""
    __slots__ = ("x", "y", "image", "scale")

    def __init__(self, x: float, y: float, image: pygame.Surface, scale: float = 1.0) -> None:
        self.x = x
        self.y = y
        self.image = image
        self.scale = scale


def render_sprites(
    screen: pygame.Surface,
    px: float,
    py: float,
    angle: float,
    sprites: Iterable[Sprite],
    depth: Sequence[Tuple[float, bool, int, float]],
    *,
    fov: float = FOV,
) -> None:
    """
    NEW: Project and draw billboards with coarse column-occlusion using depth buffer.
    """
    # Precompute for mapping screen-x -> depth index
    col_w = WIDTH / max(1, len(depth))

    # Draw far-to-near for better blending
    items: List[Tuple[float, Sprite]] = []
    for s in sprites:
        dx = s.x - px
        dy = s.y - py
        dist = math.hypot(dx, dy)
        items.append((dist, s))
    items.sort(reverse=True)

    for dist, s in items:
        # Angle to sprite
        sprite_ang = math.atan2(s.y - py, s.x - px)
        da = (sprite_ang - angle + math.pi) % (2 * math.pi) - math.pi
        if abs(da) > (fov * 0.6):  # slightly wider than FOV to allow edges to show
            continue

        # Projected height
        h = max(10, int((WALL_SIZE * 420 * s.scale) / (dist + 0.001)))
        img = pygame.transform.smoothscale(s.image, (int(h * (s.image.get_width() / s.image.get_height())), h))
        w = img.get_width()

        # Screen position
        screen_x = int((da / fov + 0.5) * WIDTH - w // 2)
        screen_y = HEIGHT // 2 - h // 2

        # Column-occlusion using depth
        # Walk across sprite columns and blit visible stripes
        for sx in range(w):
            col_x = screen_x + sx
            if 0 <= col_x < WIDTH:
                depth_idx = min(len(depth) - 1, max(0, int(col_x / col_w)))
                wall_dist = depth[depth_idx][0]
                if dist < wall_dist - 1.0:  # small epsilon to reduce z-fighting
                    # Blit one-pixel column (fast enough for small sprite count)
                    column = img.subsurface((sx, 0, 1, h))
                    screen.blit(column, (col_x, screen_y))


# --------------------------------------------------------------------------------------
# New: Mini-map and post FX
# --------------------------------------------------------------------------------------
def render_minimap(
    screen: pygame.Surface,
    game_map: Sequence[Sequence[int]],
    px: float,
    py: float,
    angle: float,
    *,
    rays: Optional[Sequence[Tuple[float, bool, int, float]]] = None,
    sprites: Optional[Iterable[Sprite]] = None,
    scale: float = 0.2,
    margin: int = 8,
) -> None:
    """
    NEW: Compact world mini-map in the top-left corner with optional rays & sprites.
    """
    map_h = len(game_map)
    map_w = len(game_map[0])
    cell = int(WALL_SIZE * scale)

    w = map_w * cell
    h = map_h * cell
    x0, y0 = margin, margin

    # Background
    pygame.draw.rect(screen, (18, 20, 22), (x0 - 2, y0 - 2, w + 4, h + 4), 0, border_radius=4)

    # Tiles
    for gy in range(map_h):
        for gx in range(map_w):
            color = (60, 60, 66) if game_map[gy][gx] else (28, 30, 36)
            pygame.draw.rect(screen, color, (x0 + gx * cell, y0 + gy * cell, cell - 1, cell - 1))

    # Player
    ptx = x0 + (px / WALL_SIZE) * cell
    pty = y0 + (py / WALL_SIZE) * cell
    pygame.draw.circle(screen, (240, 200, 80), (int(ptx), int(pty)), max(2, cell // 6))
    ex = ptx + math.cos(angle) * cell * 0.8
    ey = pty + math.sin(angle) * cell * 0.8
    pygame.draw.line(screen, (240, 200, 80), (ptx, pty), (ex, ey), 2)

    # Rays preview
    if rays:
        ray_fov = FOV
        start_ang = angle - ray_fov / 2
        step = ray_fov / max(1, len(rays))
        for i, (dist, hit, *_rest) in enumerate(rays):
            ang = start_ang + i * step
            rx = ptx + math.cos(ang) * (dist / WALL_SIZE) * cell
            ry = pty + math.sin(ang) * (dist / WALL_SIZE) * cell
            pygame.draw.aaline(screen, (70, 80, 95), (ptx, pty), (rx, ry))

    # Sprites
    if sprites:
        for s in sprites:
            sx = x0 + (s.x / WALL_SIZE) * cell
            sy = y0 + (s.y / WALL_SIZE) * cell
            pygame.draw.circle(screen, (160, 70, 70), (int(sx), int(sy)), max(2, cell // 6))


def draw_vignette(screen: pygame.Surface, alpha: int = VIGNETTE_ALPHA) -> None:
    """NEW: Subtle vignette post effect to focus the view."""
    if alpha <= 0:
        return
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    # Radial gradient approximation using concentric rects (cheap)
    steps = 10
    for i in range(steps):
        a = int(alpha * (i + 1) / steps)
        pad = int((i + 1) * (min(WIDTH, HEIGHT) * 0.03))
        pygame.draw.rect(
            overlay,
            (0, 0, 0, a),
            (0 - pad, 0 - pad, WIDTH + pad * 2, HEIGHT + pad * 2),
            width=pad * 2,
            border_radius=24
        )
    screen.blit(overlay, (0, 0))
