from sqlalchemy.orm import Session

from models.standings import Standing
from models.fixture import Fixture, FixtureStatus


class StandingsService:
    """Plain CRUD helpers over the standings table, used by the public
    and admin routers alike so the query logic only lives in one place.
    """

    @staticmethod
    def get_all(db: Session):
        return db.query(Standing).order_by(Standing.position.asc()).all()

    @staticmethod
    def get_by_team(db: Session, team_id: int):
        return db.query(Standing).filter(Standing.team_id == team_id).first()

    @staticmethod
    def get_by_season(db: Session, season_id: int):
        return (
            db.query(Standing)
            .filter(Standing.season_id == season_id)
            .order_by(Standing.position.asc())
            .all()
        )

    @staticmethod
    def get_by_competition(db: Session, competition_id: int):
        return (
            db.query(Standing)
            .filter(Standing.competition_id == competition_id)
            .order_by(Standing.position.asc())
            .all()
        )

    @staticmethod
    def create(db: Session, standing: Standing):
        db.add(standing)
        db.commit()
        db.refresh(standing)
        return standing

    @staticmethod
    def update(db: Session, standing: Standing):
        db.commit()
        db.refresh(standing)
        return standing

    @staticmethod
    def delete(db: Session, standing: Standing):
        db.delete(standing)
        db.commit()


def recompute_standings(db: Session, season_id: int, competition_id: int) -> int:
    """Rebuilds the table for one season/competition purely from the
    fixtures we already hold (status == FULLTIME).

    This is what "our own API" means for standings: there's no outside
    service to poll anymore, the table is just a derived view over the
    fixtures an admin has entered/updated. Safe to call repeatedly - it
    upserts existing Standing rows instead of duplicating them.

    Returns the number of teams whose row was written.
    """
    fixtures = (
        db.query(Fixture)
        .filter(
            Fixture.season_id == season_id,
            Fixture.competition_id == competition_id,
            Fixture.status == FixtureStatus.FULLTIME,
        )
        .all()
    )

    # team_id -> running totals
    table: dict[int, dict[str, int]] = {}

    def _row(team_id: int) -> dict[str, int]:
        return table.setdefault(
            team_id,
            {"played": 0, "wins": 0, "draws": 0, "losses": 0, "goals_for": 0, "goals_against": 0, "points": 0},
        )

    for fixture in fixtures:
        home = _row(fixture.home_team_id)
        away = _row(fixture.away_team_id)

        home["played"] += 1
        away["played"] += 1
        home["goals_for"] += fixture.home_score
        home["goals_against"] += fixture.away_score
        away["goals_for"] += fixture.away_score
        away["goals_against"] += fixture.home_score

        if fixture.home_score > fixture.away_score:
            home["wins"] += 1
            home["points"] += 3
            away["losses"] += 1
        elif fixture.home_score < fixture.away_score:
            away["wins"] += 1
            away["points"] += 3
            home["losses"] += 1
        else:
            home["draws"] += 1
            away["draws"] += 1
            home["points"] += 1
            away["points"] += 1

    # points first, goal difference breaks ties, goals scored breaks that
    ranked = sorted(
        table.items(),
        key=lambda entry: (entry[1]["points"], entry[1]["goals_for"] - entry[1]["goals_against"], entry[1]["goals_for"]),
        reverse=True,
    )

    existing = {
        standing.team_id: standing
        for standing in db.query(Standing)
        .filter(Standing.season_id == season_id, Standing.competition_id == competition_id)
        .all()
    }

    for position, (team_id, totals) in enumerate(ranked, start=1):
        goal_difference = totals["goals_for"] - totals["goals_against"]
        standing = existing.get(team_id)
        if standing is None:
            standing = Standing(season_id=season_id, competition_id=competition_id, team_id=team_id)
            db.add(standing)

        standing.position = position
        standing.played = totals["played"]
        standing.wins = totals["wins"]
        standing.draws = totals["draws"]
        standing.losses = totals["losses"]
        standing.goals_for = totals["goals_for"]
        standing.goals_against = totals["goals_against"]
        standing.goal_difference = goal_difference
        standing.points = totals["points"]

    db.commit()
    return len(ranked)
