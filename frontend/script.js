// Small currency formatter shared by the ticker/market pages (mirrors the
// one already used on clubs.html) so numbers read as "R3.0m" etc.
function formatRandShort(value) {
  if (value === null || value === undefined) return null;
  const rand = Number(value);
  const abs = Math.abs(rand);
  if (abs >= 1e9) return `R${(rand / 1e9).toFixed(1)}bn`;
  if (abs >= 1e6) return `R${(rand / 1e6).toFixed(1)}m`;
  if (abs >= 1e3) return `R${(rand / 1e3).toFixed(0)}k`;
  return `R${rand.toLocaleString('en-ZA')}`;
}

function calcAge(dateOfBirth) {
  if (!dateOfBirth) return null;
  const dob = new Date(dateOfBirth);
  if (Number.isNaN(dob.getTime())) return null;
  const diff = Date.now() - dob.getTime();
  return Math.floor(diff / (365.25 * 24 * 60 * 60 * 1000));
}

let allStandings = [];

// Builds one <option> per unique season+competition combo found in the
// standings themselves, so the dropdown never needs a separate /seasons/
// call or goes stale relative to what's actually on the table.
function populateSeasonFilter(standings) {
  const select = document.getElementById('season-filter');
  if (!select) return;

  const seen = new Map();
  standings.forEach((row) => {
    if (!row.season || !row.competition) return;
    const key = `${row.season.id}-${row.competition.id}`;
    if (!seen.has(key)) {
      const label = [row.season.label, row.competition.name].filter(Boolean).join(' — ');
      seen.set(key, label);
    }
  });

  const current = select.value;
  select.innerHTML = '<option value="all">All seasons</option>'
    + Array.from(seen.entries()).map(([key, label]) => `<option value="${key}">${label}</option>`).join('');
  if (current && Array.from(select.options).some((opt) => opt.value === current)) {
    select.value = current;
  }
}

function renderStandingsRows(standings) {
  const tbody = document.querySelector("#table-body tbody");
  if (!tbody) return;

  if (!standings.length) {
    tbody.innerHTML = `<tr><td colspan="10" class="note">No standings for this selection yet.</td></tr>`;
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
}

// The overall league leader (position 1) for the ticker on vuva.html - uses
// whichever season/competition combo appears first in the data, since the
// public /standings/ endpoint doesn't flag a "current" season explicitly.
function updateLeaderTicker(standings) {
  const leaderEl = document.getElementById('ticker-leader');
  const matchesEl = document.getElementById('ticker-matches');
  if (!leaderEl && !matchesEl) return;

  if (!standings.length) {
    if (leaderEl) leaderEl.textContent = '—';
    if (matchesEl) matchesEl.textContent = '—';
    return;
  }

  if (leaderEl) {
    const primaryKey = `${standings[0].season?.id}-${standings[0].competition?.id}`;
    const primaryTable = standings.filter((row) => `${row.season?.id}-${row.competition?.id}` === primaryKey);
    const leader = primaryTable.find((row) => row.position === 1) || primaryTable[0];
    leaderEl.textContent = leader?.team?.name || '—';
  }

  if (matchesEl) {
    const totalPlayed = standings.reduce((sum, row) => sum + (row.played || 0), 0);
    matchesEl.textContent = Math.round(totalPlayed / 2);
  }
}

// Replaces the old hardcoded "Betway Premiership · 16 clubs · 30 matches
// played each" line under the Table heading on vuva.html with the real
// competition name, club count, and matches-per-team pulled from whichever
// season/competition table appears first in the standings response.
function updateTableMeta(standings) {
  const metaEl = document.getElementById('table-meta');
  if (!metaEl) return;

  if (!standings.length) {
    metaEl.textContent = 'No standings published yet.';
    return;
  }

  const primaryKey = `${standings[0].season?.id}-${standings[0].competition?.id}`;
  const primaryTable = standings.filter((row) => `${row.season?.id}-${row.competition?.id}` === primaryKey);
  const competitionName = primaryTable[0]?.competition?.name || primaryTable[0]?.season?.label || 'League';
  const clubCount = primaryTable.length;
  const matchesEach = Math.max(...primaryTable.map((row) => row.played || 0), 0);

  metaEl.textContent = `${competitionName} · ${clubCount} club${clubCount === 1 ? '' : 's'} · ${matchesEach} match${matchesEach === 1 ? '' : 'es'} played each`;
}

async function loadStandings() {
  const tbody = document.querySelector("#table-body tbody");
  const filter = document.getElementById('season-filter');

  try {
    allStandings = await apiGet("/standings/");

    updateLeaderTicker(allStandings);
    updateTableMeta(allStandings);

    if (!tbody) return; // this page has no table, e.g. we're only here for the ticker

    if (!allStandings.length) {
      tbody.innerHTML = `<tr><td colspan="10" class="note">No standings yet — add fixture results in the admin panel, then recompute the table.</td></tr>`;
      return;
    }

    populateSeasonFilter(allStandings);
    renderStandingsRows(allStandings);

    if (filter && !filter.dataset.bound) {
      filter.dataset.bound = 'true';
      filter.addEventListener('change', () => {
        if (filter.value === 'all') {
          renderStandingsRows(allStandings);
          return;
        }
        const [seasonId, competitionId] = filter.value.split('-');
        renderStandingsRows(allStandings.filter((row) => String(row.season?.id) === seasonId && String(row.competition?.id) === competitionId));
      });
    }
  } catch (err) {
    if (tbody) tbody.innerHTML = `<tr><td colspan="10" class="note">Could not reach the VUVA API. Start the backend with uvicorn main:app --reload.</td></tr>`;
  }
}

async function loadNewsAndPlayers() {
  const ng = document.getElementById("news-grid");
  const pg = document.getElementById("player-grid");
  const mvBody = document.getElementById("mv-body");

  // Announcements - pulled from the API instead of being hardcoded. If your
  // backend doesn't expose a public GET /announcements/ endpoint yet, add
  // one (mirroring /teams/, /players/, /standings/) and this will pick it up.
  if (ng) {
    try {
      const announcements = await apiGet("/announcements/");
      ng.innerHTML = announcements.length
        ? announcements.slice(0, 6).map((item) => `
          <article class="news-card">
            <div class="news-tag">${item.announcement_type}</div>
            <div class="news-head">${item.title}</div>
            <div class="news-body">${item.summary || item.body}</div>
          </article>
        `).join('')
        : '<div class="news-card"><div class="news-head">No announcements yet</div><div class="news-body">Publish one from the admin panel and it will show up here.</div></div>';
    } catch (err) {
      ng.innerHTML = '<div class="news-card"><div class="news-head">Announcements unavailable</div><div class="news-body">Could not reach the announcements endpoint.</div></div>';
    }
  }

  if (!pg && !mvBody && !document.getElementById('ticker-scorer')) return;

  try {
    const players = await apiGet("/players/");

    function bar(label, val) {
      return `<div class="skill-row"><div class="skill-label">${label}</div><div class="skill-bar"><div class="skill-fill" style="width:${val}%"></div></div><div class="skill-val">${val}</div></div>`;
    }

    if (pg) {
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
            ${bar("Value", Math.min(99, Math.round((player.market_value_rands || 0) / 150000)))}
          </div>
          <div class="pcard-foot"><span>VUVA Index</span><span>Value R${((player.market_value_rands || 0)).toLocaleString()}</span></div>
        </div>
      `).join("");
    }

    let marketValues = [];
    if (mvBody) {
      marketValues = players
        .filter((player) => player.market_value_rands)
        .sort((a, b) => (b.market_value_rands || 0) - (a.market_value_rands || 0))
        .slice(0, 8)
        .map((player, index) => ({
          name: `${player.first_name} ${player.last_name}`,
          club: player.team_name || 'Unknown',
          pos: player.playing_position.toUpperCase(),
          value: player.market_value_rands || 0,
          rank: index + 1,
        }));

      const maxVal = Math.max(...marketValues.map((m) => m.value), 1);
      mvBody.innerHTML = marketValues.map((m) => {
        const pct = Math.round((m.value / maxVal) * 100);
        return `<tr><td class="rank">${m.rank}</td><td class="name">${m.name}</td><td class="club">${m.club}</td><td class="club">${m.pos}</td><td class="bar-cell"><div class="bar-track"><div class="bar-fill" style="width:${pct}%"></div></div></td><td class="val">${formatRandShort(m.value)}</td></tr>`;
      }).join("");

      const totalValueEl = document.getElementById('mv-total-value');
      const topValueEl = document.getElementById('mv-top-value');
      const clubsEl = document.getElementById('mv-total-clubs');
      const avgAgeEl = document.getElementById('mv-avg-age');
      if (totalValueEl) totalValueEl.textContent = formatRandShort(players.reduce((sum, p) => sum + (p.market_value_rands || 0), 0)) || 'R0';
      if (topValueEl) topValueEl.textContent = formatRandShort(marketValues[0]?.value || 0) || 'R0';
      if (clubsEl) clubsEl.textContent = new Set(players.map((p) => p.team_id)).size;
      if (avgAgeEl) {
        const ages = players.map((p) => calcAge(p.date_of_birth)).filter((age) => age !== null);
        avgAgeEl.textContent = ages.length ? (ages.reduce((sum, age) => sum + age, 0) / ages.length).toFixed(1) : '—';
      }
    }

    const scorerEl = document.getElementById('ticker-scorer');
    if (scorerEl) {
      const topScorer = players.reduce((best, p) => ((p.goals || 0) > (best?.goals || 0) ? p : best), null);
      scorerEl.textContent = topScorer ? `${topScorer.goals} goals` : '—';
    }
    const valueEl = document.getElementById('ticker-value');
    if (valueEl) {
      const topValue = Math.max(0, ...players.map((p) => p.market_value_rands || 0));
      valueEl.textContent = topValue ? formatRandShort(topValue) : '—';
    }
  } catch (error) {
    if (pg) pg.innerHTML = '';
    if (mvBody) mvBody.innerHTML = '';
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