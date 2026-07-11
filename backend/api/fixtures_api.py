from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from database.database import get_db
from models.fixture import Fixture
from models.venue import Venue
from schemas.public import FixtureOut
from services.sync_service import sync_standings_from_fixtures

router = APIRouter(prefix="/fixtures", tags=["Fixtures"])


def _to_fixture_out(db: Session, fixture: Fixture) -> FixtureOut:
    venue = db.get(Venue, fixture.venue_id)
    item = FixtureOut.model_validate(fixture)
    item.venue_name = venue.name if venue else None
    return item


@router.get("/", response_model=list[FixtureOut])
def list_fixtures(
    status: str | None = None,
    team_id: int | None = None,
    season_id: int | None = None,
    competition_id: int | None = None,
    db: Session = Depends(get_db),
):
    """Fixtures straight from our own database - upcoming matches,
    live scores and full-time results are all just rows in this table,
    entered/updated through the admin panel.
    """
    query = db.query(Fixture).options(
        joinedload(Fixture.home_team), joinedload(Fixture.away_team)
    )
    if status:
        query = query.filter(Fixture.status == status)
    if team_id is not None:
        query = query.filter((Fixture.home_team_id == team_id) | (Fixture.away_team_id == team_id))
    if season_id is not None:
        query = query.filter(Fixture.season_id == season_id)
    if competition_id is not None:
        query = query.filter(Fixture.competition_id == competition_id)

    fixtures = query.order_by(Fixture.match_datetime.asc()).all()
    return [_to_fixture_out(db, fixture) for fixture in fixtures]


@router.get("/{fixture_id}", response_model=FixtureOut)
def get_fixture(fixture_id: int, db: Session = Depends(get_db)):
    fixture = db.get(Fixture, fixture_id)
    if not fixture:
        raise HTTPException(status_code=404, detail="Fixture not found")
    return _to_fixture_out(db, fixture)


@router.post("/{fixture_id}/recompute-standings")
def recompute_standings_for_fixture(fixture_id: int, db: Session = Depends(get_db)):
    """Convenience endpoint: after a result is entered/edited for this
    fixture, recompute the table for its season/competition from the
    fixtures we hold - no external call, just our own data.
    """
    fixture = db.get(Fixture, fixture_id)
    if not fixture:
        raise HTTPException(status_code=404, detail="Fixture not found")
    synced = sync_standings_from_fixtures(db, season_id=fixture.season_id, competition_id=fixture.competition_id)
    return {"synced": synced}
