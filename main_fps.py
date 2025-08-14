import sys, math, pygame, time, random
from core.config import *
from game.team import Team
from core.scoring import ScoringSystem
from core.respawn_system import RespawnSystem
from core.team_communication import TeamCommunication
from game.player import Player
from game.enemy import Enemy
from game.projectile import Paintball
from game.game_modes import GameModes, GameMode
from game.fps import render_first_person, hitscan, WALL_SIZE
from game.fps_map import MAP

def draw_text(surface, txt, pos, size=20, color=WHITE, center=False):
    font = pygame.font.SysFont("arial", size, bold=True)
    img = font.render(txt, True, color)
    rect = img.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos
    surface.blit(img, rect)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Paintball – FPS Mode")
    clock = pygame.time.Clock()
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)

    # Systems
    scoring = ScoringSystem()
    respawns = RespawnSystem(RESPAWN_TIME)
    comms = TeamCommunication()
    modes = GameModes(GameMode.ELIMINATION)

    # Teams
    blue = Team("Blue", BLUE); red = Team("Red", RED)
    scoring.add_team(blue); scoring.add_team(red)

    # Player (Blue) – world position & camera angle
    px = 6 * WALL_SIZE + WALL_SIZE//2
    py = 6 * WALL_SIZE + WALL_SIZE//2
    player_angle = 0.0
    player = Player(px, py, "You", BLUE, blue.name)
    blue.add_player(player)

    # Enemies (Red)
    enemies = []
    for i in range(5):
        gx = random.randint(2, len(MAP[0]) - 3)
        gy = random.randint(2, len(MAP) - 3)
        ex = gx * WALL_SIZE + WALL_SIZE//2
        ey = gy * WALL_SIZE + WALL_SIZE//2
        bot = Enemy(ex, ey, f"Bot{i+1}", RED, red.name)
        red.add_player(bot)
        enemies.append(bot)

    projectiles = []  # left for compatibility
    last_time = time.time()

    # mouse sensitivity
    SENS = 0.003

    running = True
    while running:
        now = time.time()
        dt = now - last_time
        last_time = now

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                running = False
            if e.type == pygame.KEYDOWN and e.key == pygame.K_r:
                player.gun.start_reload()
            if e.type == pygame.MOUSEMOTION:
                dx, dy = e.rel
                player_angle += dx * SENS
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                # hitscan along player_angle
                if player.gun.can_fire():
                    player.gun.consume_shot()
                    hit, hx, hy, dist = hitscan(player.rect.centerx, player.rect.centery, player_angle, 1200, MAP)
                    if hit:
                        # If hitpoint overlaps an enemy, apply damage
                        for bot in enemies:
                            if bot.alive and pygame.Rect(bot.rect).inflate(-10,-10).collidepoint(hx, hy):
                                died = bot.take_hit(50)
                                if died:
                                    comms.send("System", f"You splatted {bot.name}")
                                    modes.on_frag(player.team_name, scoring)

        keys = pygame.key.get_pressed()

        # Movement in camera-space (WASD)
        mvx = (keys[pygame.K_d] - keys[pygame.K_a])
        mvy = (keys[pygame.K_w] - keys[pygame.K_s])

        cos_a = math.cos(player_angle)
        sin_a = math.sin(player_angle)
        dx = (cos_a * mvy + sin_a * mvx) * PLAYER_SPEED * dt
        dy = (sin_a * mvy - cos_a * mvx) * PLAYER_SPEED * dt

        # Grid collision vs MAP walls
        nx = player.rect.centerx + dx
        ny = player.rect.centery + dy

        # X axis
        if MAP[int(player.rect.centery // WALL_SIZE)][int(nx // WALL_SIZE)] == 0:
            player.rect.centerx = int(nx)
        # Y axis
        if MAP[int(ny // WALL_SIZE)][int(player.rect.centerx // WALL_SIZE)] == 0:
            player.rect.centery = int(ny)

        # Update systems
        player.update(dt)
        if player.gun.ammo == 0 and player.gun.reload_t <= 0:
            player.gun.start_reload()

        for bot in enemies:
            if not bot.alive:
                continue
            _ = bot.update(dt, player.center(), [])  # obstacles ignored for FPS demo

        # Respawns
        for p in respawns.update():
            if p is player:
                player.alive = True; player.hp = PLAYER_MAX_HP; player.invuln = 0.8
                player.rect.center = (6 * WALL_SIZE + WALL_SIZE//2, 6 * WALL_SIZE + WALL_SIZE//2)
            else:
                p.alive = True; p.hp = 100; p.invuln = 0.8
                p.rect.center = (random.randint(2, len(MAP[0])-3) * WALL_SIZE + WALL_SIZE//2,
                                 random.randint(2, len(MAP)-3) * WALL_SIZE + WALL_SIZE//2)

        # Render first-person
        render_first_person(screen, player.rect.centerx, player.rect.centery, player_angle, MAP, now)

        # HUD
        def hud(txt, pos, size=20, color=WHITE):
            draw_text(screen, txt, pos, size, color)
        hud(f"Blue: {scoring.get('Blue')}  Red: {scoring.get('Red')}", (20, 16), 22, WHITE)
        hud(f"HP: {max(0, player.hp)}", (20, 44), 18, GREEN)
        ammo_txt = "RELOADING..." if player.gun.reload_t > 0 else f"Ammo: {player.gun.ammo}/{player.gun.capacity}"
        hud(ammo_txt, (20, 66), 18, YELLOW)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.mouse.set_visible(True)
    pygame.event.set_grab(False)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
