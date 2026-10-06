"""Rename raw scans in images/jp to the canonical stems used by the pipeline.

    python tools/rename_scans.py          # dry run (prints the plan)
    python tools/rename_scans.py --apply  # actually rename

E.g. TD01_LEG_01.webp -> TD-01_LEG_01.webp, TD01_R_13.webp -> TD-01_R_013.webp
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JP = ROOT / "images" / "jp"


def key(s: str) -> str:
    """Loose key: uppercase, drop hyphens/underscores/spaces, strip leading zeros of digit runs."""
    s = re.sub(r"[-_\s]", "", s.upper())
    return re.sub(r"(?<=\D)0+(?=\d)", "", s)


def stem_for(card_id: str) -> str:
    return re.sub(r"\s+", "_", re.sub(r"/\d+\s*$", "", card_id.strip()))


def main() -> None:
    data = json.load(open(ROOT / "data" / "cards.json", encoding="utf-8"))
    data = data if isinstance(data, list) else data.get("cards", data)
    canon = {key(stem_for(c["id"])): stem_for(c["id"]) for c in data}
    apply = "--apply" in sys.argv
    for p in sorted(JP.glob("*.webp")):
        target = canon.get(key(p.stem))
        if target is None:
            print(f"?? no match: {p.name}")
        elif target != p.stem:
            print(f"{p.name} -> {target}.webp")
            if apply:
                p.rename(p.with_name(target + ".webp"))


if __name__ == "__main__":
    main()
