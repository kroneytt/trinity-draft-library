"""Build a Tabletop Simulator (TTS) save file (.json) for Trinity Draft.
Injects:
- Custom card deck using cards.json
- Individual card Nickname, Description (full rules/effects for tooltips), and GMNotes
- Global.lua script for drafting and pack management
- Official Card Back texture
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "cards.json"
LUA_PATH = ROOT / "tts" / "lua" / "Global.lua"
OUTPUT_SAVE = ROOT / "tts" / "TrinityDraft_Save.json"

DEFAULT_BACK = "https://raw.githubusercontent.com/kroneytt/trinity-draft-library/main/images/card_back.jpg"
DEFAULT_FRONT_BASE = "https://raw.githubusercontent.com/kroneytt/trinity-draft-library/main/images/en/"
PLAYMAT_URL = "https://raw.githubusercontent.com/kroneytt/trinity-draft-library/main/images/playmat.jpg"

RARITY_MULTIPLIERS = {
    "Legend": 1,
    "Rare": 2,
    "Uncommon": 3,
    "Common": 4,
    "Void": 9
}

def format_card_tooltip(c: dict) -> str:
    lines = []
    lines.append(f"[{c['expansion']}] {c['rarity']} | Cost: {c['cost'] or '-'} | Color: {c['color']}")
    if c.get("color_condition"):
        lines.append(f"Condition: {c['color_condition']}")
    if c.get("power") is not None:
        lines.append(f"Power: {c['power']}{c.get('power_modifier', '')} / Break: {c.get('break', '')}{c.get('break_modifier', '')}")
    if c.get("races"):
        lines.append(f"Race: {' / '.join(c['races'])}")
    lines.append("-" * 28)
    if c.get("effects"):
        lines.append(c["effects"])
    if c.get("burst_or_epic"):
        lines.append("")
        lines.append(c["burst_or_epic"])
    return "\n".join(lines)

def create_deck_obj(name, desc, cards_list, pos_x, pos_z, rot_y, start_idx):
    contained_objects = []
    deck_ids = []
    custom_deck_map = {}

    idx = start_idx
    for c in cards_list:
        idx += 1
        card_id_int = idx * 100
        deck_ids.append(card_id_int)

        front_url = f"{DEFAULT_FRONT_BASE}{c['slug']}.jpg"
        custom_deck_map[str(idx)] = {
            "FaceURL": front_url,
            "BackURL": DEFAULT_BACK,
            "NumWidth": 1,
            "NumHeight": 1,
            "BackIsHidden": True,
            "UniqueBack": False,
            "Type": 0,
        }

        contained_objects.append({
            "Name": "Card",
            "Transform": {"posX": pos_x, "posY": 2, "posZ": pos_z, "rotX": 0, "rotY": rot_y, "rotZ": 180, "scaleX": 1, "scaleY": 1, "scaleZ": 1},
            "Nickname": c["name"]["en"],
            "Description": format_card_tooltip(c),
            "GMNotes": json.dumps({"id": c["id"], "rarity": c["rarity"], "cost": c["cost"], "color": c["color"]}),
            "CardID": card_id_int,
            "CustomDeck": {str(idx): custom_deck_map[str(idx)]},
        })

    deck_obj = {
        "Name": "Deck",
        "Transform": {"posX": pos_x, "posY": 2, "posZ": pos_z, "rotX": 0, "rotY": rot_y, "rotZ": 180, "scaleX": 1, "scaleY": 1, "scaleZ": 1},
        "Nickname": name,
        "Description": desc,
        "DeckIDs": deck_ids,
        "CustomDeck": custom_deck_map,
        "ContainedObjects": contained_objects,
    }
    return deck_obj, idx

def create_playmat(player_color, pos_x, pos_z, rot_y):
    return {
        "Name": "Custom_Board",
        "Transform": {
            "posX": pos_x, "posY": 0.9, "posZ": pos_z,
            "rotX": 0, "rotY": rot_y, "rotZ": 0,
            "scaleX": 15, "scaleY": 1, "scaleZ": 15
        },
        "Nickname": f"{player_color} Playmat",
        "Locked": True,
        "CustomImage": {
            "ImageURL": PLAYMAT_URL,
            "ImageSecondaryURL": "",
            "ImageScalar": 1.0,
            "WidthScale": 0.0
        }
    }

def create_scripting_zone(name, pos_x, pos_z, rot_y):
    return {
        "Name": "ScriptingTrigger",
        "Transform": {
            "posX": pos_x, "posY": 1.5, "posZ": pos_z,
            "rotX": 0, "rotY": rot_y, "rotZ": 0,
            "scaleX": 8, "scaleY": 4, "scaleZ": 4
        },
        "Nickname": name
    }

def build_tts_save():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        cards = json.load(f)

    with open(LUA_PATH, "r", encoding="utf-8") as f:
        lua_script = f.read()

    expansions = list(set(c["expansion"] for c in cards))
    expansions.sort()

    object_states = []
    global_idx = 0

    # 3 Players: Red (bottom), Green (top-left), Blue (top-right)
    # Radius around center: ~18 units for playmats, ~10 for drafting zones
    players = [
        {"color": "Red",   "angle": 0},
        {"color": "Green", "angle": 120},
        {"color": "Blue",  "angle": 240}
    ]

    for p in players:
        a_rad = math.radians(p["angle"])
        # Playmat positions
        pm_r = 18
        pm_x = math.sin(a_rad) * pm_r
        pm_z = math.cos(a_rad) * -pm_r
        object_states.append(create_playmat(p["color"], pm_x, pm_z, p["angle"]))

        # Drafting Zones (closer to center)
        dz_r = 10
        dz_x = math.sin(a_rad) * dz_r
        dz_z = math.cos(a_rad) * -dz_r
        object_states.append(create_scripting_zone(f"DraftZone_{p['color']}", dz_x, dz_z, p["angle"]))

    # Hand Zones
    hands = []
    for p in players:
        a_rad = math.radians(p["angle"])
        h_r = 28
        hands.append({
            "Color": p["color"],
            "Transform": {
                "posX": math.sin(a_rad) * h_r,
                "posY": 4,
                "posZ": math.cos(a_rad) * -h_r,
                "rotX": 0, "rotY": p["angle"], "rotZ": 0,
                "scaleX": 15, "scaleY": 4, "scaleZ": 4
            }
        })

    # Master Pools in the center
    master_pos_offset = -3
    for exp in expansions:
        exp_cards = [c for c in cards if c["expansion"] == exp]
        draft_cards = [c for c in exp_cards if c["rarity"] != "Epic"]
        epic_cards = [c for c in exp_cards if c["rarity"] == "Epic"]

        # Build box multiset
        box_cards = []
        for c in draft_cards:
            count = RARITY_MULTIPLIERS.get(c["rarity"], 1)
            for _ in range(count):
                box_cards.append(c)

        if box_cards:
            deck, global_idx = create_deck_obj(f"Master Pool ({exp})", f"{len(box_cards)} Cards", box_cards, master_pos_offset, 0, 0, global_idx)
            # Give decks GMNotes to identify them easily in lua
            deck["GMNotes"] = f"master_pool_{exp}"
            object_states.append(deck)

        # Distribute Epics onto playmats
        if epic_cards:
            for p in players:
                a_rad = math.radians(p["angle"])
                ep_r = 22 # Outside edge of playmat
                ep_x = math.sin(a_rad) * ep_r + (master_pos_offset * math.cos(a_rad))
                ep_z = math.cos(a_rad) * -ep_r - (master_pos_offset * math.sin(a_rad))
                deck, global_idx = create_deck_obj(f"{p['color']} Epics ({exp})", "4 Epics", epic_cards, ep_x, ep_z, p["angle"], global_idx)
                object_states.append(deck)

        master_pos_offset += 6

    save_data = {
        "SaveName": "Trinity Draft - English Mod",
        "GameMode": "Trinity Draft",
        "Date": "2026",
        "Table": "Table_Hexagon",
        "LuaScript": lua_script,
        "LuaScriptState": "",
        "ObjectStates": object_states,
        "Hands": {
            "Enable": True,
            "DisableUnused": True,
            "Hiding": 1,
            "HandTransforms": hands
        }
    }

    with open(OUTPUT_SAVE, "w", encoding="utf-8") as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)

    print(f"TTS Save generated successfully at {OUTPUT_SAVE}")

if __name__ == "__main__":
    build_tts_save()
