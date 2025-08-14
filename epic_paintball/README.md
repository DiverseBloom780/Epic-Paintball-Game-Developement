# Epic Paintball (Python + Pygame)

A compact starter kit for an arcade-style paintball game made with **Pygame**. Includes:

- **Gameplay:** WASD to move, mouse to aim/shoot, paintball physics, splats, reloads, health.
- **Map:** Simple JSON tilemap with walls and spawn points.
- **AI/NPCs:** Basic bots that patrol, chase on sight, and shoot with a cooldown.
- **Customization:** Edit `data/cosmetics/default.json` or choose color in the menu.
- **UI:** Start/Pause menus, HUD with health/ammo, round timer.
- **Multiplayer (stub):** Minimal TCP server/client scaffolding to extend for online play.
- **Art/Audio:** Procedural placeholder shapes/colors; add your own sprites/sounds anytime.

> This is a learning-friendly baseline. You can ship & iterate from here.

---

## Quick Start

1. **Install Python 3.9+** (3.11 recommended).
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run**:
   ```bash
   python run_game.py
   ```

### Controls

- **WASD** – Move
- **Mouse** – Aim
- **Left Click** – Shoot
- **R** – Reload
- **ESC** – Pause / Back

### Menu Options
- Select number of bots, map, and your paint color.
- Toggle AI for quick solo matches.

---

## Project Layout

```
epic_paintball/
├─ run_game.py
├─ requirements.txt
├─ core/
│  ├─ settings.py
│  ├─ utils.py
│  └─ input.py
├─ game/
│  ├─ __init__.py
│  ├─ game.py
│  ├─ assets.py
│  ├─ player.py
│  ├─ projectile.py
│  ├─ ai.py
│  ├─ map.py
│  ├─ ui.py
│  ├─ customize.py
│  └─ networking/
│     ├─ server.py
│     └─ client.py
└─ data/
   ├─ maps/basic_map.json
   └─ cosmetics/default.json
```

---

## Multiplayer (Early Stub)

See `game/networking/server.py` and `client.py`. The server broadcasts player snapshots to all clients in a room using a simple TCP protocol (newline-delimited JSON).

**Try locally** (separate terminals):

```bash
python -m game.networking.server --host 127.0.0.1 --port 5050
python run_game.py --client 127.0.0.1:5050 --name Blue
python run_game.py --client 127.0.0.1:5050 --name Red
```

> Note: The client integration is intentionally conservative and can be toggled in the main menu (or via `--client`). Lag compensation, authoritative reconciliation, and anti-cheat are out of scope for this starter.

---

## Customize

- Change default cosmetics in `data/cosmetics/default.json` (hex colors, speeds, ammo, etc.).
- Add more maps by copying `data/maps/basic_map.json` and updating `run_game.py` menu options.

---

## Next Steps

- Replace procedural art with spritesheets & decals.
- Add real SFX and BGM (drop files into `data/sounds` and `data/music` and reference in `assets.py`).
- Implement game modes (CTF, King of the Hill, Elimination).
- Expand AI behavior trees and pathfinding (e.g., A* over navgrid).
- Build a proper matchmaking service and authoritative server.

Have fun and paint the arena! 🎨
