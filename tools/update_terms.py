import json

with open("data/cards.json", "r", encoding="utf-8") as f:
    cards = json.load(f)

for c in cards:
    # 1. Epics
    if c.get("burst_or_epic") and "add 1 chosen type from outside the game to your hand" in c["burst_or_epic"]:
        c["burst_or_epic"] = c["burst_or_epic"].replace(
            "add 1 chosen type from outside the game to your hand",
            "At the start of the game, add your chosen Epic to your hand"
        )
    
    # 2. Set -> Installation for Spell subtypes
    if c.get("type") == "Spell" and c.get("subtype") == "Set":
        c["subtype"] = "Installation"
    
    if c.get("effects"):
        # Replace [Set] with [Installation] in text
        c["effects"] = c["effects"].replace("[Set]", "[Installation]")

    # 3. Equip vs Equipment
    if c.get("type") == "Spell" and c.get("subtype") == "Equipment":
        c["subtype"] = "Equip"
    
    if c.get("effects"):
        c["effects"] = c["effects"].replace("[Equipment]", "[Equip]")

    # 4. Void Burst
    if c.get("burst_or_epic") and "Traitor" in c["burst_or_epic"]:
        c["burst_or_epic"] = c["burst_or_epic"].replace("Traitor", "Betrayal")
    
    if c.get("effects"):
        c["effects"] = c["effects"].replace("Traitor", "Betrayal")
        
with open("data/cards.json", "w", encoding="utf-8") as f:
    json.dump(cards, f, ensure_ascii=False, indent=2)

print("Terms updated.")
