import sys, math, pygame, time, random
from config import *
from team import Team
from scoring import ScoringSystem
from respawn_system import RespawnSystem
from team_communication import TeamCommunication
from obstacles import make_obstacles, draw as draw_obstacles
from player import Player
from enemy import Enemy
from projectile import Paintball
from game_modes import GameModes, GameMode

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
    pygame.display.set_caption("Paintball (Integrated)")
    clock = pygame.time.Clock()

    # Systems
    scoring = ScoringSystem()
    respawns = RespawnSystem(RESPAWN_TIME)
    comms = TeamCommunication()
    modes = GameModes(GameMode.ELIMINATION)

    # Teams
    blue = Team("Blue", BLUE); red = Team("Red", RED)
    scoring.add_team(blue); scoring.add_team(red)

    # Obstacles
    obstacles = make_obstacles()

    # Player (Blue)
    player = Player(WIDTH//2-100, HEIGHT//2, "You", BLUE, blue.name)
    blue.add_player(player)

    # Enemies (Red)
    enemies = []
    for i in range(5):
        ex = random.randint(80, WIDTH-120)
        ey = random.randint(80, HEIGHT-120)
        bot = Enemy(ex, ey, f"Bot{i+1}", RED, red.name)
        red.add_player(bot)
        enemies.append(bot)

    projectiles = []

    # Helpers
    def handle_hits():
        nonlocal projectiles
        alive = []
        for pb in projectiles:
            if not pb.alive:
                continue
            # hit players
            hit_any = False
            # skip friendly fire scoring, but still can hit (optional tweak)
            if player.alive and pb.owner is not player and pb.team_name != player.team_name:
                if pygame.Rect(player.rect).inflate(-8, -8).collidepoint(pb.pos.x, pb.pos.y):
                    died = player.take_hit(35)
                    pb.alive = False
                    hit_any = True
                    if died:
                        comms.send("System", f"{pb.owner.name} splatted You")
                        respawns.mark_dead(player)
                        modes.on_frag(pb.team_name, scoring)
            for e in enemies:
                if e.alive and pb.owner is not e and pb.team_name != e.team_name:
                    if pygame.Rect(e.rect).inflate(-8, -8).collidepoint(pb.pos.x, pb.pos.y):
                        died = e.take_hit(35)
                        pb.alive = False
                        hit_any = True
                        if died:
                            comms.send("System", f"You splatted {e.name}" if pb.owner is player else f"{pb.owner.name} splatted {e.name}")
                            modes.on_frag(pb.team_name, scoring)
            if pb.alive:
                alive.append(pb)
        projectiles = alive

    running = True
    last_time = time.time()
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
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                pb = player.try_shoot(pygame.mouse.get_pos())
                if pb: projectiles.append(pb)

        # Input movement
        keys = pygame.key.get_pressed()
        mvx = (keys[pygame.K_d] - keys[pygame.K_a])
        mvy = (keys[pygame.K_s] - keys[pygame.K_w])
        player.move((mvx, mvy), dt, obstacles)

        # Update player and enemies
        player.update(dt)
        if player.gun.ammo == 0 and player.gun.reload_t <= 0:
            player.gun.start_reload()

        for bot in enemies:
            if not bot.alive: continue
            pb = bot.update(dt, player.center(), obstacles)
            if pb: projectiles.append(pb)

        # Respawns
        for p in respawns.update():
            # simple respawn at random location
            if p is player:
                player.alive = True; player.hp = PLAYER_MAX_HP; player.invuln = 0.8
                player.rect.center = (random.randint(60, WIDTH-60), random.randint(60, HEIGHT-60))
            else:
                p.alive = True; p.hp = 100; p.invuln = 0.8
                p.rect.center = (random.randint(60, WIDTH-60), random.randint(60, HEIGHT-60))

        # Update projectiles
        bounds = pygame.Rect(0,0,WIDTH,HEIGHT)
        for pb in projectiles:
            pb.update(dt, bounds, obstacles)
        handle_hits()

        # Draw
        screen.fill(BG)
        draw_obstacles(screen, obstacles)

        # Paintballs
        for pb in projectiles:
            pb.draw(screen)

        # Entities
        if player.alive: player.draw(screen)
        for bot in enemies:
            if bot.alive: bot.draw(screen)

        # HUD
        draw_text(screen, f"Blue: {scoring.get('Blue')}  Red: {scoring.get('Red')}", (20, 16), 22, WHITE)
        draw_text(screen, f"HP: {max(0, player.hp)}", (20, 44), 18, GREEN)
        ammo_txt = "RELOADING..." if player.gun.reload_t>0 else f"Ammo: {player.gun.ammo}/{player.gun.capacity}"
        draw_text(screen, ammo_txt, (20, 66), 18, YELLOW)
        # comms
        y = HEIGHT - 20
        for msg in comms.list():
            draw_text(screen, msg, (20, y-18), 16, WHITE)
            y -= 18

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
