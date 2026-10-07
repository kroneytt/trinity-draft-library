"""Build a Tabletop Simulator (TTS) save file (.json) for Trinity Draft.
Injects:
- Custom card deck using cards.json
- Individual card Nickname, Description (full rules/effects for tooltips), and GMNotes
- Global.lua script for drafting and pack management
- Official Card Back texture
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "cards.json"
LUA_PATH = ROOT / "tts" / "lua" / "Global.lua"
OUTPUT_SAVE = ROOT / "tts" / "TrinityDraft_Save.json"

DEFAULT_BACK = "https://raw.githubusercontent.com/kroneytt/trinity-draft-library/main/images/card_back.jpg"
DEFAULT_FRONT_BASE = "https://raw.githubusercontent.com/kroneytt/trinity-draft-library/main/images/en/"

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
        lines.append(f"Power: {c['power']}{c['power_modifier']} / Break: {c['break']}{c['break_modifier']}")
    if c.get("races"):
        lines.append(f"Race: {' / '.join(c['races'])}")
    lines.append("-" * 28)
    if c.get("effects"):
        lines.append(c["effects"])
    if c.get("burst_or_epic"):
        lines.append("")
        lines.append(c["burst_or_epic"])
    return "\n".join(lines)


def create_deck_obj(name, desc, cards_list, pos_x, pos_z, start_idx):
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
            "Transform": {"posX": pos_x, "posY": 2, "posZ": pos_z, "rotX": 0, "rotY": 180, "rotZ": 180, "scaleX": 1, "scaleY": 1, "scaleZ": 1},
            "Nickname": c["name"]["en"],
            "Description": format_card_tooltip(c),
            "GMNotes": json.dumps({"id": c["id"], "rarity": c["rarity"], "cost": c["cost"], "color": c["color"]}),
            "CardID": card_id_int,
            "CustomDeck": {str(idx): custom_deck_map[str(idx)]},
        })

    deck_obj = {
        "Name": "Deck",
        "Transform": {"posX": pos_x, "posY": 2, "posZ": pos_z, "rotX": 0, "rotY": 180, "rotZ": 180, "scaleX": 1, "scaleY": 1, "scaleZ": 1},
        "Nickname": name,
        "Description": desc,
        "DeckIDs": deck_ids,
        "CustomDeck": custom_deck_map,
        "ContainedObjects": contained_objects,
    }
    return deck_obj, idx


def build_tts_save():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        cards = json.load(f)

    with open(LUA_PATH, "r", encoding="utf-8") as f:
        lua_script = f.read()

    expansions = list(set(c["expansion"] for c in cards))
    expansions.sort()

    object_states = []
    global_idx = 0

    pos_x_offset = -10

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
            deck, global_idx = create_deck_obj(f"Trinity Draft Master Pool ({exp})", f"{len(box_cards)} Draft Cards", box_cards, pos_x_offset, 0, global_idx)
            object_states.append(deck)

        # Distribute Epics
        # 3 players
        if epic_cards:
            for p in range(1, 4):
                deck, global_idx = create_deck_obj(f"Player {p} Epics ({exp})", f"4 Epics", epic_cards, pos_x_offset, 5 * p, global_idx)
                object_states.append(deck)

        pos_x_offset += 10

    save_data = {
        "SaveName": "Trinity Draft - English Mod",
        "GameMode": "Trinity Draft",
        "Date": "2026",
        "Table": "Table_Custom",
        "LuaScript": lua_script,
        "LuaScriptState": "",
        "ObjectStates": object_states,
    }

    with open(OUTPUT_SAVE, "w", encoding="utf-8") as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)

    print(f"TTS Save generated successfully at {OUTPUT_SAVE}")


if __name__ == "__main__":
    build_tts_save()
