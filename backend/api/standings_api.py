from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from database.database import get_db
from models import Competition, Season, Standing
from schemas.standings import StandingOut, SyncResponse
from services.sync_service import sync_standings_from_fixtures

router = APIRouter(prefix="/standings", tags=["Standings"])


@router.get("/", response_model=list[StandingOut])
def read_standings(
    season_id: int | None = None,
    competition_id: int | None = None,
    db: Session = Depends(get_db),
):
    """Returns a league table, ordered the way one is always read: most
    points first, goal difference breaking ties.

    Defaults to the current season if season_id isn't given. Returns an
    empty list if there's nothing in the standings table yet - that's
    not an error, it just means no admin has entered fixture results
    (or standings rows) for that season.
    """
    if season_id is None:
        season = (
            db.query(Season)
            .filter(Season.is_current == True)  # noqa: E712 - sqlalchemy needs == here, not "is"
            .first()
        )
        if not season:
            return []
        season_id = season.id

    query = (
        db.query(Standing)
        .options(joinedload(Standing.team))
        .filter(Standing.season_id == season_id)
    )
    if competition_id is not None:
        query = query.filter(Standing.competition_id == competition_id)

    return query.order_by(Standing.position.asc()).all()


@router.post("/recompute", response_model=SyncResponse)
def recompute_standings(season_id: int, competition_id: int, db: Session = Depends(get_db)):
    """Rebuilds the table for a season/competition from the full-time
    fixtures already stored in our own database - no outside service
    involved. Safe to call repeatedly; existing rows are updated in
    place rather than duplicated.
    """
    season = db.get(Season, season_id)
    if not season:
        raise HTTPException(status_code=404, detail="Season not found")
    competition = db.get(Competition, competition_id)
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")

    synced = sync_standings_from_fixtures(db, season_id=season_id, competition_id=competition_id)

    if synced == 0:
        return SyncResponse(
            synced=0,
            message="No full-time fixtures found for that season/competition yet.",
        )

    return SyncResponse(
        synced=synced,
        message=f"Recomputed standings for {synced} teams from stored fixture results.",
    )
