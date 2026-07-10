from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from database.database import get_db
from models import Standing, Season
from schemas.standings import StandingOut, SyncResponse
from services.standings_service import sync_standings

router = APIRouter(prefix="/standings", tags=["Standings"])


@router.get("/", response_model=list[StandingOut])
def read_standings(db: Session = Depends(get_db)):
    """Returns the current season's table, ordered the way a league table
    is always read: most points first, goal difference breaking ties.

    Returns an empty list if nobody has synced from TheSportsDB yet -
    that's not an error, it just means POST /api/standings/sync hasn't
    been called.
    """
    current_season = (
        db.query(Season)
        .filter(Season.is_current == True)  # noqa: E712 - sqlalchemy needs == here, not "is"
        .first()
    )
    if not current_season:
        return []

    standings = (
        db.query(Standing)
        .options(joinedload(Standing.team))
        .filter(Standing.season_id == current_season.id)
        .order_by(Standing.position.asc())
        .all()
    )
    return standings


@router.post("/sync", response_model=SyncResponse)
def refresh_standings(db: Session = Depends(get_db)):
    """Pulls the latest table from TheSportsDB and writes it into the
    database. Safe to call repeatedly - existing rows are updated in
    place rather than duplicated.
    """
    try:
        synced = sync_standings(db)
    except LookupError as error:
        # raised by sportsdb_service when the league id can't be resolved
        raise HTTPException(status_code=502, detail=str(error))

    if synced == 0:
        return SyncResponse(
            synced=0,
            message="TheSportsDB returned no table rows for the configured season.",
        )

    return SyncResponse(
        synced=synced,
        message=f"Synced {synced} teams from TheSportsDB.",
    )
