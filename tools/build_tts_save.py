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
TABLE_URL = "https://raw.githubusercontent.com/kroneytt/trinity-draft-library/main/images/table.jpg"
COMPONENT_BASE = "https://raw.githubusercontent.com/kroneytt/trinity-draft-library/main/images/components/"
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

# ---- Table geometry --------------------------------------------------------
# These are only the *starting* positions. On first load Global.lua measures a
# real card, rescales the mats so the printed card outlines match, and lays the
# table out again with the measured sizes (see layoutTable in Global.lua).
CARD_W_GUESS = 2.14                      # approx TTS card width at scale 1
MAT_W_CW = 1024 / 120                    # playmat is 8.53 card widths wide
MAT_D_CW = MAT_W_CW * 595 / 1024
SEAT_ANGLES = {"Red": 0, "Green": 120, "Blue": 240}   # rotY; Green top-left, Blue top-right


def seat_point(color, right_cw, forward_cw, y):
    """Mat-local (right, forward-towards-centre) in card widths -> world x, y, z."""
    a = math.radians(SEAT_ANGLES[color])
    rx, rz = math.cos(a), -math.sin(a)
    fx, fz = math.sin(a), math.cos(a)
    side = MAT_W_CW + 0.15
    r = (side / (2 * math.sqrt(3)) + MAT_D_CW / 2) * CARD_W_GUESS
    cx, cz = -fx * r, -fz * r
    return (cx + (rx * right_cw + fx * forward_cw) * CARD_W_GUESS, y,
            cz + (rz * right_cw + fz * forward_cw) * CARD_W_GUESS)


def create_playmat(player_color):
    # A thin Custom Tile (not a Custom Board - boards are thick wooden slabs).
    x, y, z = seat_point(player_color, 0, 0, 1.2)
    return {
        "Name": "Custom_Tile",
        "Transform": {
            "posX": x, "posY": y, "posZ": z,
            "rotX": 0, "rotY": SEAT_ANGLES[player_color], "rotZ": 0,
            "scaleX": 1, "scaleY": 1, "scaleZ": 1,   # Global.lua rescales to card size
        },
        "Nickname": f"{player_color} Playmat",
        "GMNotes": f"playmat_{player_color}",
        "Locked": True,
        "CustomImage": {
            "ImageURL": PLAYMAT_URL,
            "ImageSecondaryURL": "",
            "ImageScalar": 1.0,
            "WidthScale": 0.0,
            "CustomTile": {
                "Type": 0,          # box / rectangle
                "Thickness": 0.1,   # thin like a neoprene mat
                "Stackable": False,
                "Stretch": True,    # keep the image's 1024x595 shape
            },
        },
    }


def create_picks_zone(player_color):
    # Scripting zone over the mat's deck slot (pixel 908,307). During the draft a
    # player drops their pick here; Global.lua stacks it face down.
    x, y, z = seat_point(player_color, (908 - 512) / 120, (297.5 - 307) / 120, 2)
    return {
        "Name": "ScriptingTrigger",
        "Transform": {
            "posX": x, "posY": y, "posZ": z,
            "rotX": 0, "rotY": SEAT_ANGLES[player_color], "rotZ": 0,
            "scaleX": 1.6 * CARD_W_GUESS, "scaleY": 4, "scaleZ": 2.0 * CARD_W_GUESS
        },
        "Nickname": f"PicksZone_{player_color}",
        "GMNotes": f"pickszone_{player_color}",
    }


def create_component(name, notes, face_url, count, x, z, rot_y, start_idx, face_up=True):
    """A single card (count=1) or a deck of identical component cards (Reserve, Wall, colour cards)."""
    idx = start_idx + 1
    custom = {str(idx): {"FaceURL": face_url, "BackURL": DEFAULT_BACK, "NumWidth": 1, "NumHeight": 1,
                         "BackIsHidden": True, "UniqueBack": False, "Type": 0}}
    tr = {"posX": x, "posY": 2, "posZ": z, "rotX": 0, "rotY": rot_y, "rotZ": 0 if face_up else 180,
          "scaleX": 1, "scaleY": 1, "scaleZ": 1}
    card = {"Name": "Card", "Transform": dict(tr), "Nickname": name, "GMNotes": notes,
            "CardID": idx * 100, "CustomDeck": custom}
    if count == 1:
        return card, idx
    cards = [dict(card) for _ in range(count)]
    return {"Name": "Deck", "Transform": tr, "Nickname": name, "GMNotes": notes,
            "DeckIDs": [idx * 100] * count, "CustomDeck": custom, "ContainedObjects": cards}, idx


def create_battle_components(start_idx):
    """Reserve x3, Wall card x3, basic colour cards 4 x 16, and the Trinity Counter bag.
    Global.lua moves them to their rulebook positions (p.26-27) on first load."""
    objs, idx = [], start_idx
    # Reserve uses an English version of the card art, so no hover tooltip is needed.
    for i, c in enumerate(("Red", "Green", "Blue")):
        o, idx = create_component(f"Reserve ({c})", f"reserve_{c}", COMPONENT_BASE + "reserve_card_en.jpg", 1, -6 + 3 * i, -3, 0, idx)
        objs.append(o)
    for a, b in (("Red", "Green"), ("Green", "Blue"), ("Blue", "Red")):
        o, idx = create_component(f"Wall ({a}-{b})", f"wallcard_{a}_{b}", COMPONENT_BASE + "wall_card.jpg", 1, 0, 3, 0, idx)
        objs.append(o)
    for i, col in enumerate(("Red", "Yellow", "Purple", "Blue")):
        o, idx = create_component(f"Basic Colour: {col}", f"colordeck_{col}", COMPONENT_BASE + f"color_{col.lower()}.jpg",
                                  16, -4.5 + 3 * i, 6, 0, idx)
        objs.append(o)
    objs.append({
        "Name": "Bag", "Nickname": "Trinity Counters", "GMNotes": "counter_bag",
        "Transform": {"posX": 0, "posY": 2, "posZ": 9, "rotX": 0, "rotY": 0, "rotZ": 0,
                      "scaleX": 0.7, "scaleY": 0.7, "scaleZ": 0.7},
        "ColorDiffuse": {"r": 0.15, "g": 0.55, "b": 0.42},
        "ContainedObjects": [],
    })
    return objs, idx


def build_tts_save():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        cards = json.load(f)

    with open(LUA_PATH, "r", encoding="utf-8") as f:
        lua_script = f.read()

    expansions = list(set(c["expansion"] for c in cards))
    expansions.sort()

    object_states = []
    global_idx = 0

    players = [{"color": c} for c in ("Red", "Green", "Blue")]

    for p in players:
        object_states.append(create_playmat(p["color"]))
        object_states.append(create_picks_zone(p["color"]))

    # Hand zones behind each mat, facing the centre. Modern TTS saves define hands
    # as HandTrigger objects; the legacy "Hands" block below is kept as well.
    hands = []
    for p in players:
        x, y, z = seat_point(p["color"], 0, -(MAT_D_CW / 2 + 2.0), 4)
        object_states.append({
            "Name": "HandTrigger",
            "Transform": {
                "posX": x, "posY": y, "posZ": z,
                "rotX": 0, "rotY": SEAT_ANGLES[p["color"]], "rotZ": 0,
                "scaleX": MAT_W_CW * CARD_W_GUESS, "scaleY": 5, "scaleZ": 4,
            },
            "Nickname": f"{p['color']} Hand",
            "FogColor": p["color"],
            "Locked": True,
        })
        hands.append({
            "Color": p["color"],
            "Transform": {
                "posX": x, "posY": y, "posZ": z,
                "rotX": 0, "rotY": SEAT_ANGLES[p["color"]], "rotZ": 0,
                "scaleX": MAT_W_CW * CARD_W_GUESS, "scaleY": 5, "scaleZ": 4
            }
        })

    # Master pools side by side in the shared centre; Epics beside each deck slot.
    pool_x = {"TD-01": -0.7 * CARD_W_GUESS, "TD-02": 0.7 * CARD_W_GUESS}
    for exp in expansions:
        exp_cards = [c for c in cards if c["expansion"] == exp]
        draft_cards = [c for c in exp_cards if c["rarity"] != "Epic"]
        # The Void card ("TD ACT1 VOID") is in every box (9 copies) but cards.json
        # files it under TD-02 only, which left the TD-01 pool 9 cards short.
        if not any(c["rarity"] == "Void" for c in draft_cards):
            draft_cards += [c for c in cards if c["rarity"] == "Void"][:1]
        epic_cards = [c for c in exp_cards if c["rarity"] == "Epic"]

        box_cards = []
        for c in draft_cards:
            box_cards.extend([c] * RARITY_MULTIPLIERS.get(c["rarity"], 1))

        if box_cards:
            deck, global_idx = create_deck_obj(f"Master Pool ({exp})", f"{len(box_cards)} Cards",
                                               box_cards, pool_x.get(exp, 0), 0, 0, global_idx)
            deck["GMNotes"] = f"master_pool_{exp}"
            object_states.append(deck)

        if epic_cards:
            for p in players:
                # Separate spot per expansion so the two Epic decks don't merge.
                ex, _, ez = seat_point(p["color"], MAT_W_CW / 2 + 0.9,
                                       (297.5 - 307) / 120 + (1.6 if exp == "TD-02" else 0), 3)
                deck, global_idx = create_deck_obj(f"{p['color']} Epics ({exp})", "4 Epics", epic_cards,
                                                   ex, ez, SEAT_ANGLES[p["color"]], global_idx)
                deck["GMNotes"] = f"epics_{p['color']}_{exp}"
                object_states.append(deck)

    comps, global_idx = create_battle_components(global_idx)
    object_states.extend(comps)

    save_data = {
        "SaveName": "Trinity Draft - English Mod",
        "GameMode": "Trinity Draft",
        "Date": "2026",
        "Table": "Table_Custom",          # "Custom Rectangle" - the largest built-in table
        "TableURL": TABLE_URL,
        "LuaScript": lua_script,
        "LuaScriptState": "",
        "ObjectStates": object_states,
        "Hands": {
            "Enable": True,
            "DisableUnused": False,  # keep empty seats' hands so packs can be dealt to them
            "Hiding": 0,  # 0 = Default: only the owner sees their hand (1 = Reverse hid it from the owner)
            "HandTransforms": hands
        }
    }

    with open(OUTPUT_SAVE, "w", encoding="utf-8") as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)

    print(f"TTS Save generated successfully at {OUTPUT_SAVE}")

if __name__ == "__main__":
    build_tts_save()
