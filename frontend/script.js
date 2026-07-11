async function loadStandings() {
  const tbody = document.querySelector("#table-body tbody");
  if (!tbody) return;

  try {
    const standings = await apiGet("/standings/");
    if (!standings.length) {
      tbody.innerHTML = `<tr><td colspan="10" class="note">No standings yet — add fixture results in the admin panel, then recompute the table.</td></tr>`;
      return;
    }

    tbody.innerHTML = "";
    standings.forEach((row, i) => {
      const pos = row.position || i + 1;
      const gd = row.goal_difference;
      const tr = document.createElement("tr");
      if (pos === 1) tr.className = "zone-title";
      else if (pos <= 5) tr.className = "zone-cont";
      else if (pos >= 15) tr.className = "zone-rel";
      tr.innerHTML = `<td class="pos">${pos}</td><td class="team">${row.team.name}</td>
        <td class="num">${row.played}</td><td class="num">${row.wins}</td><td class="num">${row.draws}</td><td class="num">${row.losses}</td>
        <td class="num">${row.goals_for}</td><td class="num">${row.goals_against}</td><td class="num">${gd > 0 ? "+" + gd : gd}</td><td class="pts">${row.points}</td>`;
      tbody.appendChild(tr);
    });
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="10" class="note">Could not reach the VUVA API. Start the backend with uvicorn main:app --reload.</td></tr>`;
  }
}

async function loadNewsAndPlayers() {
  const ng = document.getElementById("news-grid");
  const pg = document.getElementById("player-grid");
  const mvBody = document.getElementById("mv-body");
  if (!ng || !pg || !mvBody) return;

  try {
    const players = await apiGet("/players/");

    ng.innerHTML = [
      {tag: "Editorial", title: "The admin now owns the league data", body: "Standings, ratings and transfer notes are managed in the dashboard so every page remains consistent."},
      {tag: "Market", title: "Values now reflect the local market", body: "Player valuation is shown in South African Rand for quicker scouting and club budgeting."},
      {tag: "Operations", title: "CRUD controls are available in one place", body: "All key entities can be created, updated and deleted from the admin panel."}
    ].map((item) => `
      <article class="news-card">
        <div class="news-tag">${item.tag}</div>
        <div class="news-head">${item.title}</div>
        <div class="news-body">${item.body}</div>
      </article>
    `).join("");

    function bar(label, val) {
      return `<div class="skill-row"><div class="skill-label">${label}</div><div class="skill-bar"><div class="skill-fill" style="width:${val}%"></div></div><div class="skill-val">${val}</div></div>`;
    }

    pg.innerHTML = players.slice(0, 6).map((player) => `
      <div class="pcard">
        <div class="pcard-top">
          <div>
            <div class="pcard-name">${player.first_name} ${player.last_name}</div>
            <div class="pcard-role">${player.playing_position.toUpperCase()} — ${player.team_name || player.team_id}</div>
          </div>
          <div class="pcard-index">${player.overall_rating || 0}</div>
        </div>
        <div class="pcard-body">
          ${bar("Form", Math.round(player.form_rating || 70))}
          ${bar("Potential", Math.round(player.potential_rating || 70))}
          ${bar("Goals", Math.min(99, (player.goals || 0) * 4 + 40))}
          ${bar("Value", Math.min(99, Math.round((player.market_value_rands || 0) / 150000))) }
        </div>
        <div class="pcard-foot"><span>VUVA Index</span><span>Value R${((player.market_value_rands || 0)).toLocaleString()}</span></div>
      </div>
    `).join("");

    const marketValues = players
      .filter((player) => player.market_value_rands)
      .sort((a, b) => (b.market_value_rands || 0) - (a.market_value_rands || 0))
      .slice(0, 8)
      .map((player, index) => ({
        name: `${player.first_name} ${player.last_name}`,
        club: player.team_name || 'Unknown',
        pos: player.playing_position.toUpperCase(),
        value: (player.market_value_rands || 0) / 1000000,
        rank: index + 1,
      }));

    const maxVal = Math.max(...marketValues.map((m) => m.value), 1);
    mvBody.innerHTML = marketValues.map((m) => {
      const pct = Math.round((m.value / maxVal) * 100);
      return `<tr><td class="rank">${m.rank}</td><td class="name">${m.name}</td><td class="club">${m.club}</td><td class="club">${m.pos}</td><td class="bar-cell"><div class="bar-track"><div class="bar-fill" style="width:${pct}%"></div></div></td><td class="val">R${(m.value * 10000000).toLocaleString()}</td></tr>`;
    }).join("");

    const totals = document.querySelectorAll('.mv-stat .mv-num');
    if (totals.length) {
      totals[0].textContent = `R${(players.reduce((sum, player) => sum + (player.market_value_rands || 0), 0) ).toLocaleString()}`;
      totals[3].textContent = `R${((marketValues[0]?.value || 0) * 10000000).toLocaleString()}`;
    }
  } catch (error) {
    ng.innerHTML = '<div class="news-card"><div class="news-head">Content unavailable</div><div class="news-body">Start the backend to see announcements and player insights.</div></div>';
    pg.innerHTML = '';
    mvBody.innerHTML = '';
  }
}

loadStandings();
loadNewsAndPlayers();

function showPage(id) {
  document.querySelectorAll("section.page").forEach((section) => section.classList.remove("active"));
  const target = document.getElementById(id);
  if (target) target.classList.add("active");
  document.querySelectorAll("nav.links a").forEach((link) => link.classList.toggle("active", link.getAttribute("href") === `${id}.html` || link.dataset.page === id));
  window.scrollTo({ top: 0, behavior: "smooth" });
}

if (document.querySelectorAll("nav.links a").length) {
  document.querySelectorAll("nav.links a").forEach((link) => {
    link.addEventListener("click", (event) => {
      const href = link.getAttribute("href");
      if (href && href.endsWith('.html')) {
        return;
      }
      event.preventDefault();
      showPage(link.dataset.page || link.getAttribute("href"));
    });
  });
}

document.querySelectorAll(".qn-card").forEach((card) => {
  card.addEventListener("click", () => showPage(card.dataset.goto));
});