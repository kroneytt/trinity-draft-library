document.addEventListener("DOMContentLoaded", () => {
  let allCards = [];
  let activeColors = new Set(["Red", "Yellow", "Blue", "Purple", "Colorless"]);

  const grid = document.getElementById("card-grid");
  const countBadge = document.getElementById("card-count");
  const searchInput = document.getElementById("search");
  const raceSelect = document.getElementById("race-select");
  const sortSelect = document.getElementById("sort-select");
  const resetBtn = document.getElementById("reset-filters");
  const modal = document.getElementById("card-modal");
  const modalBody = document.getElementById("modal-body");
  const modalClose = document.querySelector(".modal-close");

  fetch("data/cards.json")
    .then(r => r.json())
    .then(cards => {
      allCards = cards;
      populateRaces(cards);
      renderCards();
    })
    .catch(err => {
      countBadge.innerText = "Error loading card database.";
      console.error(err);
    });

  function populateRaces(cards) {
    const races = new Set();
    cards.forEach(c => (c.races || []).forEach(r => races.add(r)));
    Array.from(races).sort().forEach(r => {
      const opt = document.createElement("option");
      opt.value = r;
      opt.textContent = r;
      raceSelect.appendChild(opt);
    });
  }

  function getChecked(name) {
    return Array.from(document.querySelectorAll(`input[name="${name}"]:checked`)).map(el => el.value);
  }

  function renderCards() {
    const term = searchInput.value.trim().toLowerCase();
    const exp = getChecked("expansion");
    const rarities = getChecked("rarity");
    const types = getChecked("type");
    const race = raceSelect.value;
    const sortVal = sortSelect.value;

    let filtered = allCards.filter(c => {
      if (!exp.includes(c.expansion)) return false;
      if (!rarities.includes(c.rarity)) return false;
      if (!types.includes(c.type)) return false;

      // Color filter
      const cardColors = c.color.split("/").map(s => s.trim());
      const hasColor = cardColors.some(col => activeColors.has(col));
      if (!hasColor) return false;

      // Race filter
      if (race && !(c.races || []).includes(race)) return false;

      // Text search
      if (term) {
        const hay = [
          c.id,
          c.name.en,
          c.name.ja,
          c.name.literal,
          c.effects,
          c.burst_or_epic,
          (c.races || []).join(" ")
        ].join(" ").toLowerCase();
        if (!hay.includes(term)) return false;
      }
      return true;
    });

    // Sort
    filtered.sort((a, b) => {
      if (sortVal === "id_asc") return a.id.localeCompare(b.id);
      if (sortVal === "id_desc") return b.id.localeCompare(a.id);
      if (sortVal === "cost_asc") return (a.cost || 0) - (b.cost || 0);
      if (sortVal === "cost_desc") return (b.cost || 0) - (a.cost || 0);
      if (sortVal === "power_desc") return (b.power || 0) - (a.power || 0);
      return 0;
    });

    countBadge.innerText = `Showing ${filtered.length} of ${allCards.length} cards`;
    grid.innerHTML = "";

    filtered.forEach(c => {
      const el = document.createElement("div");
      el.className = "card-box";
      el.onclick = () => showModal(c);

      el.innerHTML = `
        <div class="card-header">
          <span class="card-id-badge">${c.id}</span>
          <span class="card-rarity rarity-${c.rarity}">${c.rarity}</span>
        </div>
        <div class="card-title">${c.name.en}</div>
        <div class="card-ja-title">${c.name.ja}</div>
        <div class="card-stats">
          <span><strong>Cost:</strong> ${c.cost !== null ? c.cost : "-"}</span>
          ${c.power !== null ? `<span><strong>Power:</strong> ${c.power}${c.power_modifier}</span>` : ""}
          ${c.break !== null ? `<span><strong>Break:</strong> ${c.break}${c.break_modifier}</span>` : ""}
        </div>
        ${c.races && c.races.length ? `<div class="card-races">${c.races.join(" / ")}</div>` : ""}
        <div class="card-effects">${c.effects ? escapeHtml(c.effects) : "<em>No effect text</em>"}</div>
        ${c.burst_or_epic ? `<div class="card-burst">${escapeHtml(c.burst_or_epic)}</div>` : ""}
      `;
      grid.appendChild(el);
    });
  }

  function showModal(card) {
    modalBody.innerHTML = `
      <div style="display: flex; gap: 24px; flex-wrap: wrap;">
        <div style="flex: 1 1 300px; min-width: 260px;">
          <div style="background: #111; border-radius: 8px; padding: 12px; text-align: center;">
            <p style="color: #888; font-size: 0.85rem; margin-bottom: 8px;">Card Scan / Preview</p>
            <img src="images/en/${card.slug}.jpg" alt="${card.name.en}" 
                 onerror="if(!this.dataset.s){this.dataset.s=1;this.src='../images/en/${card.slug}.jpg';}else if(this.dataset.s==1){this.dataset.s=2;this.src='images/jp/${card.slug}.webp';this.alt='Japanese Scan';}else{this.onerror=null;this.src='../images/jp/${card.slug}.webp';}" 
                 style="width: 100%; max-width: 340px; border-radius: 8px; box-shadow: 0 4px 16px rgba(0,0,0,0.5);">
          </div>
        </div>
        <div style="flex: 2 1 340px;">
          <h2 style="font-size: 1.4rem; color: #ffd548; margin-bottom: 4px;">${card.name.en}</h2>
          <p style="color: #aaa; font-size: 0.95rem; margin-bottom: 12px;">${card.name.ja} (${card.name.literal})</p>
          
          <div style="display: flex; gap: 12px; margin-bottom: 16px; font-size: 0.9rem; background: #121215; padding: 10px; border-radius: 6px;">
            <div><strong>ID:</strong> ${card.id}</div>
            <div><strong>Expansion:</strong> ${card.expansion}</div>
            <div><strong>Rarity:</strong> <span class="rarity-${card.rarity}">${card.rarity}</span></div>
            <div><strong>Color:</strong> ${card.color}</div>
          </div>

          <div style="display: flex; gap: 16px; margin-bottom: 16px; font-size: 0.95rem;">
            <div><strong>Cost:</strong> ${card.cost !== null ? card.cost : "-"}</div>
            ${card.power !== null ? `<div><strong>Power:</strong> ${card.power}${card.power_modifier}</div>` : ""}
            ${card.break !== null ? `<div><strong>Break:</strong> ${card.break}${card.break_modifier}</div>` : ""}
            <div><strong>Type:</strong> ${card.type}${card.subtype ? ` (${card.subtype})` : ""}</div>
          </div>

          ${card.races && card.races.length ? `<p style="margin-bottom: 12px; color: #ffd548;"><strong>Race:</strong> ${card.races.join(" / ")}</p>` : ""}

          <div style="margin-bottom: 16px;">
            <h3 style="font-size: 0.95rem; text-transform: uppercase; color: #888; margin-bottom: 6px;">Effects</h3>
            <div style="line-height: 1.5; background: #121215; padding: 12px; border-radius: 6px;">
              ${card.effects ? escapeHtml(card.effects) : "<em>None</em>"}
            </div>
          </div>

          ${card.burst_or_epic ? `
            <div>
              <h3 style="font-size: 0.95rem; text-transform: uppercase; color: #888; margin-bottom: 6px;">Burst / Epic Rule</h3>
              <div style="line-height: 1.5; background: #121215; padding: 12px; border-radius: 6px; color: #ffa07a;">
                ${escapeHtml(card.burst_or_epic)}
              </div>
            </div>
          ` : ""}
        </div>
      </div>
    `;
    modal.classList.remove("hidden");
  }

  function escapeHtml(str) {
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  modalClose.onclick = () => modal.classList.add("hidden");
  modal.querySelector(".modal-backdrop").onclick = () => modal.classList.add("hidden");

  // Filter Event Listeners
  searchInput.addEventListener("input", renderCards);
  raceSelect.addEventListener("change", renderCards);
  sortSelect.addEventListener("change", renderCards);
  document.querySelectorAll('input[type="checkbox"]').forEach(el => el.addEventListener("change", renderCards));

  document.querySelectorAll(".chip-btn").forEach(btn => {
    btn.onclick = () => {
      const c = btn.dataset.color;
      if (activeColors.has(c)) {
        activeColors.delete(c);
        btn.classList.remove("active");
      } else {
        activeColors.add(c);
        btn.classList.add("active");
      }
      renderCards();
    };
  });

  resetBtn.onclick = () => {
    searchInput.value = "";
    raceSelect.value = "";
    sortSelect.value = "id_asc";
    activeColors = new Set(["Red", "Yellow", "Blue", "Purple", "Colorless"]);
    document.querySelectorAll(".chip-btn").forEach(b => b.classList.add("active"));
    document.querySelectorAll('input[type="checkbox"]').forEach(c => c.checked = true);
    renderCards();
  };
});
