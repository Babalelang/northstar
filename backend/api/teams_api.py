from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.database import get_db
from schemas.public import TeamOut
from services.teams_service import TeamsService

router = APIRouter(prefix="/teams", tags=["Teams"])


@router.get("/", response_model=list[TeamOut])
def list_teams(country: str | None = None, db: Session = Depends(get_db)):
    """All clubs we track, straight from our own teams table."""
    return TeamsService.get_all(db, country=country)


@router.get("/{team_id}", response_model=TeamOut)
def get_team(team_id: int, db: Session = Depends(get_db)):
    team = TeamsService.get_by_id(db, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team
