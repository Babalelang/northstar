import os

from models import Team, Competition, Season, Standing
from services import sportsdb_service

# fixed identifiers for the one competition this project tracks. these
# aren't "seed data" in the sense of pre-filled match/player rows - they're
# just the lookup keys get_or_create_competition uses to find or create a
# single Competition row, the same way you'd hardcode a slug anywhere else
COMPETITION_CODE = "RSA-PSL"
COMPETITION_NAME = "South African Premiership"


def _season_label_from_env():
    """Turns the .env season format ("2025-2026") into a display label
    ("2025/26"), matching what the frontend already expects.
    """
    raw = os.getenv("SPORTSDB_SEASON", "2025-2026")
    start, end = raw.split("-")
    return f"{start}/{end[2:]}"


def get_or_create_competition(db):
    competition = (
        db.query(Competition)
        .filter(Competition.code == COMPETITION_CODE)
        .first()
    )
    if competition:
        return competition

    competition = Competition(
        name=COMPETITION_NAME,
        short_name="Premiership",
        code=COMPETITION_CODE,
        country="South Africa",
        governing_body="PSL",
        tier=1,
    )
    db.add(competition)
    db.flush()  # assigns competition.id without needing a full commit yet
    return competition


def get_or_create_season(db, competition, label):
    season = (
        db.query(Season)
        .filter(Season.label == label, Season.competition_id == competition.id)
        .first()
    )
    if season:
        return season

    season = Season(
        label=label,
        is_current=True,
        competition_id=competition.id,
    )
    db.add(season)
    db.flush()
    return season


def get_or_create_team(db, name, badge_url):
    team = db.query(Team).filter(Team.name == name).first()
    if team:
        # badge can change or arrive later than the team itself did
        if badge_url and not team.logo_url:
            team.logo_url = badge_url
        return team

    team = Team(name=name, country="South Africa", logo_url=badge_url)
    db.add(team)
    db.flush()
    return team


def _to_int(value, default=0):
    """TheSportsDB returns most numeric fields as strings, and some as
    null when a season hasn't started - this keeps the sync from blowing
    up on either case.
    """
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def sync_standings(db):
    """Pulls the current table from TheSportsDB and upserts it into the
    standings table. Returns the number of rows synced.

    This is meant to be called from the /api/standings/sync endpoint, or
    from scripts/sync_standings.py on a schedule (cron, task scheduler,
    etc). It does not insert any data that didn't come back from the api.
    """
    season_label = _season_label_from_env()
    sportsdb_season = os.getenv("SPORTSDB_SEASON", "2025-2026")

    rows = sportsdb_service.get_league_table(sportsdb_season)
    if not rows:
        return 0

    competition = get_or_create_competition(db)
    season = get_or_create_season(db, competition, season_label)

    synced = 0
    for row in rows:
        team = get_or_create_team(db, row.get("strTeam"), row.get("strBadge"))

        standing = (
            db.query(Standing)
            .filter(
                Standing.season_id == season.id,
                Standing.competition_id == competition.id,
                Standing.team_id == team.id,
            )
            .first()
        )
        if not standing:
            standing = Standing(
                season_id=season.id,
                competition_id=competition.id,
                team_id=team.id,
            )
            db.add(standing)

        standing.position = _to_int(row.get("intRank"))
        standing.played = _to_int(row.get("intPlayed"))
        standing.wins = _to_int(row.get("intWin"))
        standing.draws = _to_int(row.get("intDraw"))
        standing.losses = _to_int(row.get("intLoss"))
        standing.goals_for = _to_int(row.get("intGoalsFor"))
        standing.goals_against = _to_int(row.get("intGoalsAgainst"))
        standing.goal_difference = _to_int(row.get("intGoalDifference"))
        standing.points = _to_int(row.get("intPoints"))
        standing.form = row.get("strForm")

        synced += 1

    db.commit()
    return synced
