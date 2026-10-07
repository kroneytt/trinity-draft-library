# Trinity Draft Tabletop Simulator Implementation Plan

## 1. Feasibility: Triangular Seating & Playmats
**Yes, this is entirely feasible.**
Tabletop Simulator allows us to define custom positions and rotations for both Hand Zones (where players physically sit/view the table) and physical objects like Playmats.
- **Seating:** We will configure a custom table. The 3 players (e.g., Red, Green, Blue) will be positioned at the bottom, top-left, and top-right, facing the center.
- **Playmats:** We will import the playmat image you provided as a "Custom Token" or "Custom Board". We will spawn 3 of these playmats, scale them to correctly fit standard TTS card sizes, and lock them in place directly in front of each player's seat, rotated so they face the player.
- **Epics & Tokens:** We will automatically place each player's 4 Epics, Reserve, and 3 Walls directly onto the corresponding designated zones of their playmat.

## 2. Table & Asset Setup
To make this work seamlessly, the Python generator (`build_tts_save.py`) will be updated to output a comprehensive save state that includes:
- **3 Hand Zones:** `Red` (0°), `Green` (120°), and `Blue` (-120°).
- **3 Playmats:** Using your uploaded playmat image.
- **Master Pools:** TD-01 and TD-02 Master Decks (351 cards each) stored securely in the center.
- **Epic Sets:** Separated by expansion and dealt to the players at start.
- **Drafting Zones:** Invisible scripting zones in front of each player where packs will appear.

## 3. Automation Script (`Global.lua`)
We will replace the placeholder Lua script with a fully functional draft manager.

### Phase A: Expansion Selection & Setup
- A central UI panel will ask the host: **"Select Draft Set: TD-01 or TD-02"**.
- Upon selection, the script retrieves the chosen Master Deck and shuffles it.
- It distributes the 4 Epics of that expansion to each player's playmat.

### Phase B: The Draft Loop
- **Pool Management:** A box is 351 cards. A 3-player draft requires 9 packs of 13 cards (117 cards). This means exactly 3 drafts can be played from one box before needing a reshuffle.
- **Round Start:** 
  - The script pulls 39 cards from the deck and creates 3 packs of 13.
  - One pack is placed in each player's Drafting Zone.
- **Drafting & Passing:** 
  - Players look through their pack, pick 1 card, and drag it to their hand (or a "Drafted Cards" zone).
  - Players click a personal UI button hovering over their pack: **"Pass"**.
  - Once all 3 players click Pass, the script teleports the remaining cards to the next player.
  - **Direction:** Round 1 (Clockwise), Round 2 (Anti-clockwise), Round 3 (Clockwise).
- **End of Round:** When a pack reaches 0 cards, the next round starts automatically, dealing 3 new packs of 13 cards.
- **End of Draft:** After 3 rounds (9 packs), the draft concludes. Players build their decks.

### Phase C: Continuation Options
- Once a draft ends, a UI panel will appear with two options:
  1. **Continue (Next Draft):** Starts a new draft using the *remaining* 234 cards in the Master Deck. (If the deck is empty, it forces a reshuffle).
  2. **Reshuffle & Restart:** Returns all cards to the Master Deck, shuffles the full 351 cards, and starts a fresh draft from the top.

## 4. Next Steps
If you approve this flow, I will:
1. Update `build_tts_save.py` to embed your playmat, generate the triangular table seating, hand zones, and scripting zones.
2. Write the complete Tabletop Simulator Lua script (`Global.lua`) to handle the entire drafting logic, UI buttons, and card movement.
3. Push the new save file to GitHub for you to test.
