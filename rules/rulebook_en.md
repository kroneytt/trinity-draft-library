# Trinity Draft — English Rulebook (ACT1 BLAZE & ACT1 PHANTOM)

Translated from the official Japanese rulebooks (`blaze.pdf`, `phantom.pdf`, 23 spreads each, printed pp. 04–47).
The two books share **identical rules** (pp. 04–21, 26–47 are the same apart from artwork and the sample cards shown).
Differences are the epic introductions (pp. 22–25) and the card-specific Q&A (p. 46–47); both are covered at the end.

> Translation notes: terms follow `data/glossary.yaml`. Text on small sample cards in the books is not translated here
> (it lives in `cards.json`). Page numbers are the printed numbers.

---

## 0. Set-up (pp. 06–09)

### Contents (per box, 3 players)
| Item | Qty | Purpose |
|---|---|---|
| Reserve | 3 | Where each player keeps their Trinity Counters (up to 10). Holds the abilities to gain counters / convert them into draws. |
| Wall cards / Walls | 3 / 3 | Protective "barrier" for your Life. Dealing damage pushes the wall; when damage gets past the wall it hits Life. |
| Trinity Counters | 30 | Paid for/used by Reserve and card effects; gained through Reserve ability or card/Burst effects. |
| Play sheets | 3 | Show where cards go in battle; back side has card-reading help. (Optional) |
| Colour cards | 4 types × 16 | Energy source. Rest to pay costs; gain by Colour Charge. Red, Blue, Yellow, Purple. |
| Epic cards | 4 types × 3 | Your "chosen trump card". Chosen at build time, hidden from opponents. |
| Draft cards | 351 (123 types) | The main cards. You may only play cards you drafted. |

Card numbers in a box: `TD-0x LEG 01/20–20/20`, `R 001/102–020/102`, `U 021/102–066/102`, `C 067/102–102/102`, `TD ACT1 VOID`, Epics `X 01/04–04/04`.

### Generating packs (p. 08–09)
- 4 rarities + the special card **Void** (Epics are not used). Rarity is printed on the left edge of the card.
- 123 types / 351 cards: **Legend** 1 each = 20 (holo) · **Rare** 2 each = 40 (foil) · **Uncommon** 3 each = 138 · **Common** 4 each = 144 · **Void** 9 copies of 1 card = 9.
- Shuffle all 351 face-down, occasionally check that Rares/Legends and identical cards aren't clumped, stack in **13-card packs**.
- One play = **9 packs** (3 per player); 27 packs max (= exactly 3 plays per box).
- A printable "real pack sheet" is available on the official site (optional).

---

## 1. Draft (pp. 10–19)

### Before starting
Before the draft, each player is given one of each of the 4 Epic cards (Red, Yellow, Blue, Purple) — "one of each colour per player". The Epic you will actually bring is chosen later, at battle set-up.

### Draft flow (pp. 10–11)
1. Open your own pack (everyone takes 1 pack).
2. Repeat **A–D until no cards remain to pass**:
   A. Look at the contents and choose 1 card. B. Place it face-down in front of you.
   C. Make the rest a face-down bundle. D. Pass to the neighbour / receive from the neighbour.
   - Pack 1: pass **clockwise**; pack 2: **counter-clockwise**; pack 3: **clockwise**.
3. Check the cards you've taken (you will have 13), then open your next pack. **Do this 3 times.** → 39 cards.

Tip: don't mix your picked cards with the cards still in the pack.

### Rarity introduction (p. 12)
- **Legend** – 1 copy each; unique cards with game-deciding power. *Always take.*
- **Rare** – 2 copies; strong; the core of a deck. *"Build a winning deck."*
- **Uncommon** – 3 copies; convenient, combo pieces; active early, a little extra late.
- **Common** – 4 copies; "actually full of strong cards". Burst-less commons have uncommon-or-better stats.
- **Void** – 9 copies; has a *negative* Burst that hurts you; poor stats. Don't take it (it stays to the end, remember who took it).
- Rare Void Assassin has a Void-like negative Burst — advanced-only.

### Role of drafted cards (p. 13)
All 39 cards become **two decks** — no card is unused.
- **Main Deck – 23 cards**: units, spells; the normal deck. Normally build in **2 colours** (3 at most; 4 makes costs hard to meet).
- **Life Deck – 16 cards**: when you take damage, the top card flips and its **Burst** may trigger. Colour/cost don't matter for Burst. Cards that didn't make the Main Deck often go here.

### How to read cards (pp. 14–15)
Card parts: ① Cost ② Colour Condition ③ Expansion mark ④ Card number ⑤ Colour ⑥ Rarity ⑦ Type ⑧ Race (units) ⑨ Card name ⑩ Abilities ⑪ Special ability ⑫ Power / Break ⑬ Burst ⑭ Equip bonus.

| Card type | Summary |
|---|---|
| **Unit** | Pay cost to summon onto the battlefield. Has Power/Break; attacks/blocks. |
| **Spell – Equip** | Pay cost to use → placed on battlefield. Can attach (Equip cost) to a unit to raise Power/Break. |
| **Spell – Set** *(設置)* | Pay cost to use → placed on battlefield; effects work while it stays there. |
| **Spell – Shot** | Pay cost, resolve effect, then go to the graveyard. |
| **Shadow card** | Usable even during the opponent's turn; **no cost** (counts as 0 when referenced); has a usage condition; counts as Spell **and** Unit if it is a unit. |

**Two ways to use a card:** ① **Colour Charge** (once per turn: discard a card, take 1 basic colour card of its colour; multicolour = pick one; colourless cannot charge). ② **Pay the cost** (cost at top-left, Colour Condition at centre: rest colour cards that satisfy it).

**Shadow:** *Set* – in Main Phase, put a card from hand face-down in a Shadow Zone slot (max 3). *Use* – usable from the turn it is set, once its condition is met; also during Attack / opponent's turn. Normally the Shadow Zone only holds Shadow cards (a few effects put others there).

### Reading abilities (pp. 16–17)
**Auras** (units): **Quick Aura** – can attack the turn it entered. **Bad Aura** – if it loses a battle, the opposing unit is destroyed. **Sky Aura** – can't be blocked except by Sky Aura units. **Steel Aura** (スチールオーラ) – attacks hit Life directly regardless of Walls.

**First icons (timing):** **On Entry** (登場時) – enters battlefield (any method). **On Attack** (アタック時) – when it attacks. **On Destroy** (破壊時) – when destroyed on the battlefield. **Trigger** (誘発) – effect stated happens at the timing described. **Activate** (起動) – Main Phase, optional, use at will. **Continuous** (常時) – while on the battlefield.

**Condition bar:** if a condition exists you can't do the lower part without meeting it. `<Optional>` – you choose whether to use. Format: `Keyword condition — description`. Colour-pay marks / turn-limit marks ("Turn 1": once per turn, "Turn 2": twice per turn).

**Special abilities:** **Shinra Summon** (神羅召喚) – stack on units whose total cost equals the number; no cost paid. **ZERO Summon** – cost 0 and colour condition ignored when conditions are met. **Reduced Summon** (軽減召喚) – cost reduced under a condition (colour condition unchanged). **Jigoku Back** (ジゴクバック) – when placed in the graveyard from the deck, enters the battlefield without paying. **Colour Charge-like "Oni Charge"** (鬼チャージ) – bonus effect that triggers when used for colour charge; **must** be used if it applies. **Colour Shift** – send a unit from your battlefield to the graveyard to produce colour/extra cost when summoning.

**Keyword conditions** (cost keywords): **Overdrive** – when near winning (total damage dealt to opponents' Life). **Overcount** – counts Trinity Counters in your Reserve. **Soul Flare** – send cards from under the card (Soul) to the graveyard. **Counter Flare** – remove Trinity Counters (they return to the counter zone). **Bloody Drive** – deal damage to your own Wall (pick a Favourable wall). **Counter Vortex** – remove all (max 10) counters. **Life Eater** (ライフイーター) – activates when the attack deals damage to the opponent's Life; once; not usable before the Burst check. **Requiem** (鎮魂) – activates by counting units sent to graveyard this turn. **Abyss Gate** – put cards from your graveyard into Soul. **Alchemy** (錬金) – destroy your own Equip/Set (Phantom-only). **Combine** (合体) – put matching-race cards into Soul to power up.

**Then / "If you do":** continue only if the preceding requirement was met. **Search** – look through your deck for the specified card, add to hand, shuffle.

**Active / Rest:** vertical = Active, horizontal = Rest. Acting cards become Rest.

### How to use abilities (pp. 18–19)
- **Trinity Counter:** gained by Reserve ability (pay 3 colour cost → 1 counter, once per turn; max 10) or card/Burst effects. **3 counters = 1 draw.**
- **Soul Flare:** Soul = cards under a card. Pay by sending Soul to the graveyard (your choice).
- **Shinra Summon:** choose your battlefield units whose costs add up exactly; stack the new card on top; the underlying cards become Soul. Key points: same cost → can overlay a single card; resting units can be stacked and the new unit enters *Active*; like a normal summon it can't attack the turn it appears.
- **Equip:** ① pay card cost → enters battlefield. ② Use Activate "Equip: Pay N colours" → attach to one of your units (can stack equips). Equipped unit gets Power/Break. Equipment stays when the unit leaves.
- **Favourable / Unfavourable (Wall condition):** a wall on the opponent's side = **Favourable**; on your side = **Unfavourable**. There are 3 wall slots between you and each opponent; combos [1 fav/1 unfav], [2/0], [0/2]. Bloody Drive requires ≥1 Favourable wall; you take the damage on it ("when damage is dealt" effects apply).
- **Combine:** put the specified number of matching units into Soul; power/break go up, you gain Quick Aura.
- **Jigoku Back:** enters from deck→graveyard (e.g. "send top card of deck to graveyard", "search deck to graveyard", "reveal/check top card, send it").
- **Colour Shift:** send units to the graveyard as part of summoning to produce colour; combine with Reduced Summon; no on-destroy because it isn't a destruction.

---

## 2. Build (pp. 20–25)

Use **all 39 cards** to build two decks:
- **Main Deck: 23 cards** + 1 Epic that you chosen at battle set-up (Epic isn't counted in the 23).
- **Life Deck: 16 cards**.
Guideline cost spread in the Main Deck: cost **0–2: 7 cards, 3–4: 10 cards, 5+: 6 cards**; keep ≥15 units.

---

## 3. Battle (pp. 26–37)

### Set-up (pp. 26–27)
0. **Decide turn order** (e.g. rock-paper-scissors); play proceeds clockwise.
1. **Place Reserve** in front of you, centre of the play sheet.
2. **Choose 1 Epic and set it face-down** (hand, hidden). Keep the others out of sight.
3. **Colour cards & Counters:** basic colour cards + Trinity Counters go in the centre ("colour card zone" and "counter zone").
4. **Place Walls** between players (diagonal front-left/right). First player starts with *1 wall on the left-hand side*; 2nd player: left wall; 3rd player: left/right (both walls favourable for the 3rd).
5. **Split the Life Deck** in two (shuffle the 16, split 8/8) and place them left and right of you, horizontally.
6. **Place the Main Deck** (23, shuffled) at the right edge; leave a card-width gap for the graveyard.

Tip: the Epic chosen is secret until summoned. 3rd player: acts later but starts with Walls Favourable and can use Bloody Drive from the start.

### Start declaration (p. 28)
All players draw **5** from the Main Deck. Shout **"Awakening! Trinity Draft!"** (アウェイキング！トリニティドラフト！): add the set-aside Epic to your hand and start. *The first player also draws on turn 1.*

### Victory and basics (p. 30)
**Win = deal 12 damage to opponents' Life** (when your two gained-Life zones total **12** cards, you win).
Zones: Reserve · your Life (2 decks) · Gained Life · Battlefield (units/sets/equips) · Main Deck · Graveyard · Shadow Zone (3 slots) · Colour Zone.
**Epic cards never go to the graveyard** – whenever they would (destroyed, discarded, Colour-charged…) they return to the Main Deck and it is shuffled.

### Turn flow (pp. 32–33)
1. **Draw Phase** – normal draw (everyone from turn 1). *Rise:* if the deck is empty, shuffle the graveyard into a new deck, then draw 3 instead.
2. **Active Phase** – set all your battlefield and Colour-zone cards Active.
3. **Main Phase 1** (any order, any number): Colour Charge (once/turn) · Reserve effects (**Trinity Charge**: pay 3 → 1 counter, once/turn; **Trinity Draw**: pay 3 counters → draw 1) · use/summon cards · set Shadow · Activate.
4. **Attack Phase** (units that entered this turn can't attack).
5. **Main Phase 2** – same as Main Phase 1. (Colour Charge only once per turn across both main phases.)
6. **End Phase** – End-of-turn effects.

### Attack Phase flow (pp. 34–35)
1. **Declare attack** (or decline → end the phase). Choose one opponent; Rest one Active unit and attack.
2. Opponent may use "on attack" timing; the attacked player may **block** with an Active unit (Rest it) or not.
3. **Block:** compare Power; higher wins, lower is destroyed; tie → both destroyed. Then **Attack end** → can declare another attack.
4. **No block:** **Damage = Break value.** Damage moves the Wall toward the defender; each damage pushes the wall 1 slot. When damage reaches the end, it hits the Life Deck one damage at a time: **Burst check** per damage. If the Burst triggers, resolve it. Revealed life cards go to the opponent's Gained Life. Remaining damage continues with the next Burst check.
5. **Vanish Burn** (バニッシュバーン): when Life reaches 0 — remaining damage is erased, walls pushed back to the opposite side (not damage), then Burst is resolved. (Win requires 12.)
- Life must be taken **at least 4** from a single opponent to reach 12; conversely if you hold ≥4 you can't be beaten by that opponent.

### Burst effects (p. 37) – examples
Can only be used when the card is flipped from the Life Deck. Typical: *"This turn you can't attack."* / *"Go straight to Main Phase 2; remaining damage is cancelled."* / *"Draw/return coloured card"*. **VOID:** its Burst ("Traitor/裏切り") deals you an additional damage if revealed in a Burst check.

---

## 4. Detailed rules (pp. 38–39)

- **Same-timing effects** are stacked; resolved from the last stacked (top) first. Within your own effects you choose the order; between players, the **later turn-order player stacks later**. Players pass in turn; if everyone passes, resolution begins.
- **Destroyed cards don't go to the graveyard immediately.** They move to the *judgement area* (still counted as destroyed); the Soul goes to the graveyard; the card goes to the graveyard when all stacked effects are done.
- **Shadow:** can be used at the condition's timing; a *shot* shadow is counted as going to graveyard from hand once used. If an attack's first resolution has already happened there is no further "on attack" timing in that attack.
- A triggered effect still resolves even if its source left the battlefield, unless a condition/cost requires it.
- **Condition bar timing:** `Optional` is chosen when stacked; **costs/judgements are paid/checked at execution**, not at stacking.
- A **2-player ruleset** is published on the official site; 3 players are not required.

---

## 5. Rules Q&A (pp. 40–47)

**Condition bars / "If you do"** – If you can't do the full number demanded (e.g. "discard 2" with 1 in hand), "if you do"/after-▶ effects can't be used. Condition costs/judgements happen on execution; Optional choices on stacking; you can't choose "do" if you can't pay; conditions only need to be met at judgement.

**Areas:** battlefield excludes Shadow/Colour Zone/Reserve and Soul. No limit on battlefield, hand, Colour-zone card counts; hand size is public.
**Reserve:** Trinity Charge once per turn in total (not once per Main Phase). Trinity Draw works with an empty deck (you just can't draw). Trinity Counters: capped at 10; counts as an increase/decrease relative to the previous number.
**Deck:** no Rise during a draw effect; with 1 card, "send 2 to the graveyard" sends 1; *Check* = only you see, *Reveal* = everyone sees; Jigoku Back works if the card was checked/revealed on its way to the graveyard.
**Life deck:** you can't choose which 8 are left/right; Epics can't be in the Life Deck.
**Processing:** *Destroy* ≠ *Send from battlefield to graveyard* (the latter skips the judgement area; no On Destroy). *Take damage* (e.g. Bloody Drive) doesn't hit Life; *Deal damage* is the attack kind. Walls can only be moved with the opposing player's pair. Using "from ▶" ignores the condition bar before it. Colour-Charged cards go to the graveyard before the basic colour card is added; Epic returns to deck instead. **Oni Charge** triggers in the graveyard, before the colour card is added, and **must** be used.
**Hit:** break raised after the attack hit Life doesn't add damage.
**Burst check:** if damage remains after pushing the wall back, Burst checks continue; unwanted Burst is optional unless it says otherwise; the Gained Life isn't updated until after the Burst; "Immediately Main Phase 2" Burst puts a card into the opponent's Gained Life, cancels remaining damage; **Vanish Burn** damage isn't "damage taken"; a final **VOID** card still deals its "Traitor" damage after the wall moves.
**Battle:** a unit that loses is destroyed simultaneously with the win/lose decision, moves to the judgement area; Soul goes to the graveyard; Bad Aura and On Destroy resolve afterwards.
**Epic:** a destroyed Epic returns to the deck; Epic counts as "sent to graveyard" for cost payments; discarded Epic returns to the deck before any "then/if you do".
**Units:** power changed on the battlefield reverts after leaving; a unit with "Doesn't leave when destroyed" at 0 Power stays at 0; Shadow units can be chosen as units; "put onto battlefield" costs nothing.
**Equip:** can't swap to the same unit; Shinra-summoning over an equipped unit drops the equipment.
**Shot (used from hand):** goes to the graveyard after effects resolve; conditional shots can be used paying cost (but conditional effects won't fire).
**Shadow:** can raise a Shadow unit's cost (from 0); count as both unit and spell; usable as Shinra cost (adds only Soul count); for "cost ≤3" targets, Shadow counts as 0.
**Special summons:** Shinra unit can't attack the turn it enters unless it has Quick Aura; it enters Active even if the cost card was Rest; ZERO Summon only in your own Main Phase (not on the opponent's turn); Reduced Summon still requires the colour cost; cost changes happen at "cost change" timing after the declaration: *declare (reveal) → confirm cost → cost change → colour payment → enters*. Colour Shift is used at the colour-payment step; left-over colour can't be used for another summon; Reduced Summon + multiple Colour Shifts are allowed.
**Soul Flare:** you choose which Soul card to send.
**Bloody Drive:** one use cannot split damage between left and right wall — choose one Favourable wall.
**Requiem:** counts destroyed units and units sent to the graveyard (not Soul/Shadow Zone); Epic returns to the deck but still counts.
**Combine:** a unit can combine only once while on the battlefield; it doesn't revert after the souls are lost; later-entering units don't get earlier power-ups.
Other: a card's owner = who had it at game start; cards under control revert to the owner's zones (Soul excepted). A unit that loses Quick Aura before declaring cannot attack.

---

## 6. Expansion-specific content

### ACT1 BLAZE (blaze.pdf)
Epics (pp. 22–25):
| Epic | Colour | Theme |
|---|---|---|
| Extreme Emperor Dragon God, Blazeroar Dragon (極天皇竜神 ブレイズロア・ドラゴン) | Red | Soul Flare destroys everything; removal + draw; Shinra summon engine. +1 colour partners: Voracious Fiend, Dragon-Soul Legion, Rhin's Underground City (Blue). |
| Azure-Awakened Emperor Dragon, Abyss Sturm (蒼醒皇竜 アビスストルム) | Blue | Gather an army and ram through undead bodies; destruction-immune units; Reduced Summon. Partners: Ferocious Tiger Warrior, Aqua Transformation Art, Death Cut (Purple). |
| Aristia, the Extreme Holy Empress Princess (極聖皇姫 アリスティア) | Yellow | Create sanctuary by changing counters; destruction-resistant; goddess-class field holder. Partners: Guard Sneaker, Baby Light Dragon, Shadow Ritual (Purple). |
| Emperor Dragon of the End, Zerobafam (終焉の皇竜 ゼロバファム) | Purple | Overdrive; ZERO Summon; "bring victory from any situation". Partners: Red Little Dragon (Red), Frankengirl, Black War Princess Lamiel. |
Q&A highlights (p. 46–47): Aristia can't save a unit destroyed together with a counter-add ("increase +1 counter" on destroy resolves after it left); Blazeroar's summon colours count; Abyss Gate–Shot rulings; Abyss Sturm "can't be chosen" rules.

### ACT1 PHANTOM (phantom.pdf)
Identical rules; art/names differ.
| Epic | Colour | Theme |
|---|---|---|
| Phantom Zwei Dragon, the Curse Emperor Dragon (呪皇竜 ファントムツヴァイ ドラゴン) | Purple | "Curse strike" from graveyard; ZERO Summon via Shot count; Abyss Gate. Partners: Innocent Feast, Fincar's Selector, Break Shot (Red). |
| Nexus, the Soaring Machine Emperor (機皇天翔 ネクサス) | Yellow | **5-unit Combine "Nexus Earth"**; Overdrive; threat of Break. Partners: Layfeet Cornerstone, Observer Meisin, Blue Star Sinister (Blue). |
| Last Clock, the Star-Guiding Dragon Machine Emperor (星導竜機皇 ラストクロック) | Blue | Chain extra turns; Counter Vortex finisher. Partners: Spark Knife, Famous Dog Kotetsu, House-seeking Crab (Yellow). |
| Advent Kaiser, the Flashing Dragon Princess Emperor (瞬く竜姫皇 アドベントカイザー) | Red | Quick Aura + Overdrive; chain dragons from the deck. Partners: Young Water Dragon, Strong Impact, Dragon Girl Ryan. |
Phantom Q&A (p. 46–47) additions: Last Clock "extra turn" means a second turn immediately after this one; Nexus/Combine rules; Phantom Zwei's effect choice; Shadow-spell usage ignores the condition; "damage that doesn't hit Life" (Overdrive effect); "Dreadnought" destroy-3 count includes Shadow Zone; etc.
