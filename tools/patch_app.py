import re

with open("site/js/app.js", "r", encoding="utf-8") as f:
    js = f.read()

# Replace the sorting logic
new_sort = """    const rarityRank = { "Epic": 6, "Legend": 5, "Rare": 4, "Uncommon": 3, "Common": 2, "Void": 1 };

    // Sort
    filtered.sort((a, b) => {
      if (sortVal === "id_asc") {
        if (a.expansion !== b.expansion) return a.expansion.localeCompare(b.expansion);
        const rankA = rarityRank[a.rarity] || 0;
        const rankB = rarityRank[b.rarity] || 0;
        if (rankA !== rankB) return rankB - rankA;
        return a.id.localeCompare(b.id);
      }
      if (sortVal === "id_desc") {
        if (a.expansion !== b.expansion) return b.expansion.localeCompare(a.expansion);
        const rankA = rarityRank[a.rarity] || 0;
        const rankB = rarityRank[b.rarity] || 0;
        if (rankA !== rankB) return rankA - rankB;
        return b.id.localeCompare(a.id);
      }
      if (sortVal === "cost_asc") return (a.cost || 0) - (b.cost || 0);
      if (sortVal === "cost_desc") return (b.cost || 0) - (a.cost || 0);
      if (sortVal === "power_desc") return (b.power || 0) - (a.power || 0);
      return 0;
    });"""

js = re.sub(r"// Sort[\s\S]*?return 0;\n\s+\}\);", new_sort, js)

with open("site/js/app.js", "w", encoding="utf-8") as f:
    f.write(js)

print("Patched app.js")
