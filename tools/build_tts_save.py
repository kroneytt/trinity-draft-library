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


def build_tts_save():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        cards = json.load(f)

    with open(LUA_PATH, "r", encoding="utf-8") as f:
        lua_script = f.read()

    # Filter draftable cards (Exclude Epics for master pool deck)
    draft_cards = [c for c in cards if c["rarity"] != "Epic"]
    epic_cards = [c for c in cards if c["rarity"] == "Epic"]

    contained_objects = []
    deck_ids = []
    custom_deck_map = {}

    for idx, c in enumerate(draft_cards, start=1):
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
            "Transform": {"posX": 0, "posY": 1, "posZ": 0, "rotX": 0, "rotY": 180, "rotZ": 180, "scaleX": 1, "scaleY": 1, "scaleZ": 1},
            "Nickname": c["name"]["en"],
            "Description": format_card_tooltip(c),
            "GMNotes": json.dumps({"id": c["id"], "rarity": c["rarity"], "cost": c["cost"], "color": c["color"]}),
            "CardID": card_id_int,
            "CustomDeck": {str(idx): custom_deck_map[str(idx)]},
        })

    master_deck_obj = {
        "Name": "Deck",
        "Transform": {"posX": 0, "posY": 2, "posZ": 0, "rotX": 0, "rotY": 180, "rotZ": 180, "scaleX": 1, "scaleY": 1, "scaleZ": 1},
        "Nickname": "Trinity Draft Master Pool",
        "Description": f"{len(draft_cards)} Draft Cards (Excludes Epics)",
        "DeckIDs": deck_ids,
        "CustomDeck": custom_deck_map,
        "ContainedObjects": contained_objects,
    }

    save_data = {
        "SaveName": "Trinity Draft - English Mod",
        "GameMode": "Trinity Draft",
        "Date": "2026",
        "Table": "Table_Custom",
        "LuaScript": lua_script,
        "LuaScriptState": "",
        "ObjectStates": [
            master_deck_obj
        ],
    }

    with open(OUTPUT_SAVE, "w", encoding="utf-8") as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)

    print(f"TTS Save generated successfully at {OUTPUT_SAVE}")
    print(f"Total cards in pool: {len(draft_cards)} | Epics separated: {len(epic_cards)}")


if __name__ == "__main__":
    build_tts_save()
