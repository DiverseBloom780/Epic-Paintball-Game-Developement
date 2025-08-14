import pygame
from core import settings as S
from core.config import WHITE

def draw_text(surf, text, pos, size=24, color=S.WHITE, center=False):
    font = pygame.font.SysFont("arial", size, bold=True)
    img = font.render(text, True, color)
    rect = img.get_rect()
    rect.center = pos if center else pos
    if not center:
        surf.blit(img, pos)
    else:
        surf.blit(img, rect)

def draw_hud(surf, player, time_left):
    # Health bar
    pygame.draw.rect(surf, (50,50,60), (20, 20, 250, 18), border_radius=6)
    hpw = int(250 * max(0, player.health) / S.PLAYER_MAX_HEALTH)
    pygame.draw.rect(surf, (64,220,120), (20, 20, hpw, 18), border_radius=6)
    draw_text(surf, f"HP: {int(player.health)}", (26, 20), 18)

    # Ammo
    pygame.draw.rect(surf, (50,50,60), (20, 48, 250, 18), border_radius=6)
    amw = int(250 * player.ammo / max(1, player.max_ammo))
    pygame.draw.rect(surf, (255,210,64), (20, 48, amw, 18), border_radius=6)
    draw_text(surf, f"Ammo: {player.ammo}/{player.max_ammo}", (26, 48), 18)

    # Timer
    draw_text(surf, f"Time: {time_left:0.1f}s", (S.SCREEN_WIDTH-160, 20), 22)

def draw_menu(surf, state):
    surf.fill((20,22,26))
    draw_text(surf, "EPIC PAINTBALL", (S.SCREEN_WIDTH//2, 100), 64, (255,255,255), True)
    draw_text(surf, "[ENTER] Start  |  [+/-] Bots: {}  |  [C] Color".format(state["bots"]), (S.SCREEN_WIDTH//2, 220), 26, (220,220,220), True)
    draw_text(surf, "[M] Toggle AI: {}  |  [1] Basic Map  |  [Q] Quit".format("ON" if state["ai"] else "OFF"), (S.SCREEN_WIDTH//2, 260), 24, (200,200,200), True)
    draw_text(surf, "Selected Color", (S.SCREEN_WIDTH//2, 320), 24, (200,200,200), True)
    pygame.draw.circle(surf, state["color"], (S.SCREEN_WIDTH//2, 370), 24)