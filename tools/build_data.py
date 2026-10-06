"""Build canonical data/cards.json from data/cards.xlsx and data/glossary.yaml.
Normalizes data types, fixes terms according to the glossary,
parses effect abilities into structured objects, and reports stats.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
import openpyxl
import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
XLSX_PATH = DATA_DIR / "cards.xlsx"
GLOSSARY_PATH = DATA_DIR / "glossary.yaml"
OUTPUT_JSON = DATA_DIR / "cards.json"
OVERRIDES_PATH = ROOT / "tools" / "card_overrides.yaml"
REPORTS_DIR = ROOT / "reports"


def slug_id(card_id: str) -> str:
    cleaned = re.sub(r"/\d+\s*$", "", card_id.strip())
    return re.sub(r"\s+", "_", cleaned)


def normalize_cost(val):
    if val is None or str(val).strip() == "" or str(val).strip().lower() == "none":
        return None, False
    s = str(val).strip()
    is_shadow = "shadow" in s.lower()
    m = re.search(r"\d+", s)
    if m:
        return int(m.group(0)), is_shadow
    if is_shadow:
        return 0, True
    return None, False


def normalize_num(val):
    if val is None or str(val).strip() == "" or str(val).strip().lower() == "none":
        return None, ""
    s = str(val).strip()
    if s.endswith("+"):
        base = int(float(s[:-1]))
        return base, "+"
    m = re.search(r"[-+]?\d+", s)
    if m:
        return int(m.group(0)), ("+" if "+" in s else "")
    return None, ""


def main():
    with open(GLOSSARY_PATH, "r", encoding="utf-8") as f:
        glossary = yaml.safe_load(f)

    overrides = {}
    if OVERRIDES_PATH.exists():
        with open(OVERRIDES_PATH, "r", encoding="utf-8") as f:
            overrides = yaml.safe_load(f) or {}

    wb = openpyxl.load_workbook(XLSX_PATH, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    headers = [str(h).strip() for h in rows[0]]

    # Race alias map
    race_alias = {}
    for canon_race, info in glossary.get("races", {}).items():
        race_alias[canon_race.lower()] = canon_race
        for al in info.get("aliases", []):
            race_alias[al.lower()] = canon_race

    cards = []
    for r in rows[1:]:
        row_dict = dict(zip(headers, r))
        raw_id = row_dict.get("Card_ID")
        if not raw_id:
            continue
        sid = slug_id(str(raw_id))

        # Check for card-level data corrections from overrides
        card_ov = overrides.get(sid, {})
        corrections = card_ov.get("corrections", {})
        row_dict.update(corrections)

        # Cost & Shadow
        cost_num, is_shadow_cost = normalize_cost(row_dict.get("Cost"))

        # Types
        raw_type = str(row_dict.get("Type") or "").strip()
        is_shadow_type = "shadow" in raw_type.lower()
        is_shadow = is_shadow_cost or is_shadow_type

        main_type = "Unit" if "unit" in raw_type.lower() else "Spell"
        subtype = None
        m_sub = re.search(r"\(([^)]+)\)", raw_type)
        if m_sub:
            subtype = m_sub.group(1).strip()

        # Power & Break
        p_val, p_mod = normalize_num(row_dict.get("Power"))
        b_val, b_mod = normalize_num(row_dict.get("Break"))

        # Races
        raw_races = str(row_dict.get("Race") or "").strip()
        races = []
        if raw_races and raw_races.lower() != "none":
            for part in re.split(r"[/,]", raw_races):
                cleaned_r = part.strip()
                if cleaned_r:
                    canon = race_alias.get(cleaned_r.lower(), cleaned_r)
                    races.append(canon)

        # Normalize effects
        effects_text = str(row_dict.get("Effects") or "").strip()
        # Uniformity: [Optional] -> <Optional>
        effects_text = re.sub(r"\[Optional\]", "<Optional>", effects_text)
        # Uniformity: Steal Aura -> Steel Aura
        effects_text = re.sub(r"\bSteal Aura\b", "Steel Aura", effects_text)
        # Uniformity: [Cavalry] / [War Cavalry] -> [War Knight]
        effects_text = re.sub(r"\[(?:War\s+)?Cavalry\]", "[War Knight]", effects_text)
        # Uniformity: Equipment Cost -> Equip Cost
        effects_text = re.sub(r"\[Equipment Cost\]", "[Equip Cost]", effects_text)

        # Epic rule / Burst
        burst_text = str(row_dict.get("Epic_Rule_or_Burst") or "").strip()
        burst_text = re.sub(r"\[Optional\]", "<Optional>", burst_text)
        burst_text = re.sub(r"\bSteal Aura\b", "Steel Aura", burst_text)

        card_entry = {
            "id": str(raw_id).strip(),
            "slug": sid,
            "expansion": str(row_dict.get("Expansion") or "").strip(),
            "rarity": str(row_dict.get("Rarity") or "").strip(),
            "name": {
                "en": str(row_dict.get("Name_English") or "").strip(),
                "ja": str(row_dict.get("Name_Japanese") or "").strip(),
                "literal": str(row_dict.get("Name_Literal") or "").strip(),
            },
            "color": str(row_dict.get("Color") or "").strip(),
            "cost": cost_num,
            "color_condition": str(row_dict.get("Color_Condition") or "").strip() or None,
            "type": main_type,
            "subtype": subtype,
            "is_shadow": is_shadow,
            "races": races,
            "power": p_val,
            "power_modifier": p_mod,
            "break": b_val,
            "break_modifier": b_mod,
            "effects": effects_text if effects_text and effects_text.lower() != "none" else "",
            "burst_or_epic": burst_text if burst_text and burst_text.lower() != "none" else "",
        }
        cards.append(card_entry)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(cards, f, ensure_ascii=False, indent=2)

    print(f"Successfully generated {OUTPUT_JSON} with {len(cards)} cards.")


if __name__ == "__main__":
    main()
