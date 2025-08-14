import os, sys, json, argparse, pygame
from core import settings as S
from game.game import Game
from game import ui
from game.customize import load_cosmetics
from game.networking.client import NetClient

def load_map(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def menu(screen):
    clock = pygame.time.Clock()
    state = {"bots": 3, "ai": True, "color": (64,160,255), "client": None, "name": "Player"}
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return None
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    return state
                if e.key == pygame.K_q:
                    return None
                if e.key == pygame.K_PLUS or e.key == pygame.K_EQUALS:
                    state["bots"] = min(12, state["bots"]+1)
                if e.key == pygame.K_MINUS:
                    state["bots"] = max(0, state["bots"]-1)
                if e.key == pygame.K_m:
                    state["ai"] = not state["ai"]
                if e.key == pygame.K_c:
                    # cycle through colors
                    choices = [(64,160,255),(64,220,120),(255,210,64),(220,64,64),(200,120,255)]
                    idx = (choices.index(state["color"])+1) % len(choices) if state["color"] in choices else 0
                    state["color"] = choices[idx]
        ui.draw_menu(screen, state)
        pygame.display.flip()
        clock.tick(60)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--client", default=None, help="host:port to join server (optional)")
    ap.add_argument("--name", default="Player")
    args = ap.parse_args()

    pygame.init()
    screen = pygame.display.set_mode((S.SCREEN_WIDTH, S.SCREEN_HEIGHT))
    pygame.display.set_caption("Epic Paintball (Starter)")
    pygame.mouse.set_visible(True)

    # Load cosmetics (override color if provided by file)
    cos = load_cosmetics(os.path.join("data","cosmetics","default.json"))
    def parse_hex(h): 
        h = h.lstrip("#"); return tuple(int(h[i:i+2],16) for i in (0,2,4))
    color = parse_hex(cos.get("player_color","#40A0FF"))

    # Menu
    state = menu(screen)
    if state is None:
        pygame.quit(); return
    if state["color"]: color = state["color"]

    # Map
    mp = load_map(os.path.join("data","maps","basic_map.json"))

    # Optional net client
    net = None
    if args.client:
        host, port = args.client.split(":")
        net = NetClient(host, int(port), name=args.name)

    game = Game(screen, mp, player_color=color, bot_count=state["bots"], ai_enabled=state["ai"])

    # Simple net integration: broadcast your position; print others
    clock = pygame.time.Clock()
    running = True
    while running and game.round_time > 0:
        dt = clock.tick(S.FPS) / 1000.0
        running = game.update(dt)
        game.draw()

        # net send/poll
        if net:
            net.send_snapshot(game.local_player.name, float(game.local_player.pos.x), float(game.local_player.pos.y))
            for msg in net.poll():
                if msg.get("type") == "snapshot":
                    # minimal demo: draw tiny marker
                    x, y = msg.get("x",0), msg.get("y",0)
                    pygame.draw.circle(screen, (255,255,255), (int(x), int(y)), 4)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
