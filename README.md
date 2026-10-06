# Trinity Draft - English Card Library & TTS Mod Project

This repository provides an English resource suite and Tabletop Simulator (TTS) mod for the Japanese card game **Trinity Draft** (https://trinitydraft.com/).

---

## Project Structure

```
trinity-draft-library/
├── data/
│   ├── cards.xlsx            # Source card spreadsheet
│   ├── cards.json            # Canonical normalized database (253 cards)
│   └── glossary.yaml         # Rules terminology and keyword mappings
├── images/
│   ├── jp/                   # Japanese raw scans (e.g. TD-01_LEG_01.webp)
│   ├── en/                   # Generated English overlaid card images
│   └── card_back.jpg         # Extracted official card back
├── site/                     # Static English card library website (GitHub Pages)
│   ├── index.html
│   ├── css/style.css
│   ├── js/app.js
│   └── data/cards.json
├── tts/                      # Tabletop Simulator assets
│   ├── TrinityDraft_Save.json # TTS save file with custom deck & Lua scripts
│   └── lua/Global.lua        # Table script for automated drafting
└── tools/
    ├── build_data.py         # Normalizes cards.xlsx -> cards.json
    ├── make_card_images.py   # Renders English overlays on scans
    ├── build_tts_save.py     # Generates TTS save file
    └── card_overrides.yaml   # Per-card layout & corrections
```

---

## 1. English Card Library Website
To test the website locally:
```bash
cd site
python -m http.server 8000
```
Open your browser at `http://localhost:8000`. You can search cards, filter by color/rarity/type/expansion, and click any card to inspect full details and translations.

---

## 2. Tabletop Simulator (TTS) Setup
1. Copy `tts/TrinityDraft_Save.json` into your local Tabletop Simulator Saves directory:
   - **Windows**: `%USERPROFILE%\Documents\My Games\Tabletop Simulator\Saves\`
2. Launch Tabletop Simulator and open your saved games list to load **Trinity Draft - English Mod**.
3. Use the on-table buttons:
   - **Start 3P Draft**: Automates pack distribution (9 packs of 13 cards) and handles rotation.
   - **Pass Packs**: Rotates remaining cards to the next player.

---

## 3. Adding New Card Scans
1. Place scanned card images into `images/jp/` named by card number (e.g. `TD-01_LEG_02.webp`).
2. Run the image generation pipeline:
   ```bash
   .\.venv\Scripts\python.exe tools\make_card_images.py
   ```
3. Re-run `tools/build_tts_save.py` to update the TTS mod.
