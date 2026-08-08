from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_db
from models import Season
from schemas.public import SeasonOut

router = APIRouter(prefix="/seasons", tags=["Seasons"])


@router.get("/", response_model=list[SeasonOut])
def list_seasons(competition_id: int | None = None, db: Session = Depends(get_db)):
    """Every season we have on record, most recent first - this is what
    populates the season dropdown on statistics.html (and anywhere else
    that needs to let a visitor pick a season). Public/unauthenticated,
    unlike /admin/seasons.
    """
    query = db.query(Season)
    if competition_id is not None:
        query = query.filter(Season.competition_id == competition_id)
    return query.order_by(Season.start_date.desc()).all()