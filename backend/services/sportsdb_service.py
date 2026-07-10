import os
from dotenv import load_dotenv
import requests

# loaded again here (database.py already does this) so this module also
# works if it's ever imported/run on its own, e.g. from a standalone script
load_dotenv()

API_KEY = os.getenv("SPORTSDB_API_KEY", "123")
BASE_URL = f"https://www.thesportsdb.com/api/v1/json/{API_KEY}"

# league id gets resolved once per process and cached here, so a sync
# that pulls the table and then the teams doesn't do the same lookup twice
_resolved_league_id = None


def _get(path, params=None):
    """Thin wrapper around requests.get for TheSportsDB.

    Raises requests.HTTPError on a bad response so the caller (the sync
    service) can decide how to handle it, instead of silently returning
    half-broken data.
    """
    response = requests.get(f"{BASE_URL}/{path}", params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def resolve_league_id():
    """Finds the South African Premiership's TheSportsDB league id.

    If SPORTSDB_LEAGUE_ID is set in .env, that's used directly and no
    network call is made. Otherwise this searches TheSportsDB's full list
    of soccer leagues for a South African match, so nothing is hardcoded
    to an id that might be wrong or might change.
    """
    global _resolved_league_id

    env_id = os.getenv("SPORTSDB_LEAGUE_ID")
    if env_id:
        return env_id

    if _resolved_league_id:
        return _resolved_league_id

    data = _get("search_all_leagues.php", params={"s": "Soccer"})
    leagues = data.get("countrys") or data.get("leagues") or []

    for league in leagues:
        name = (league.get("strLeague") or "").lower()
        country = (league.get("strCountry") or "").lower()
        if "south africa" in country and "premier" in name:
            _resolved_league_id = league.get("idLeague")
            return _resolved_league_id

    raise LookupError(
        "Could not find the South African Premiership in TheSportsDB's "
        "league list. Set SPORTSDB_LEAGUE_ID in .venv/.env to skip this "
        "lookup and pin it manually."
    )


def get_league_table(season):
    """Returns the raw table rows for a given season, e.g. season="2025-2026".

    Each row looks roughly like:
    {idTeam, strTeam, strBadge, intRank, intPlayed, intWin, intDraw,
     intLoss, intGoalsFor, intGoalsAgainst, intGoalDifference, intPoints,
     strForm}
    """
    league_id = resolve_league_id()
    data = _get("lookuptable.php", params={"l": league_id, "s": season})
    return data.get("table") or []
