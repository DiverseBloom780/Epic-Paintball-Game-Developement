import json

def load_cosmetics(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"player_color":"#40A0FF"}
