from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.database import get_db
from models import Team
from schemas.public import PlayerOut
from services.players_service import PlayersService

router = APIRouter(prefix="/players", tags=["Players"])


def _to_player_out(db: Session, player) -> PlayerOut:
    team = db.get(Team, player.team_id)
    item = PlayerOut.model_validate(player)
    item.team_name = team.name if team else None
    return item


@router.get("/", response_model=list[PlayerOut])
def list_players(
    team_id: int | None = None,
    position: str | None = None,
    db: Session = Depends(get_db),
):
    """Every player in our own database, optionally filtered by team or
    playing position - this is what the players/market/statistics pages
    render from, no outside source involved.
    """
    players = PlayersService.get_all(db, team_id=team_id, position=position)
    return [_to_player_out(db, player) for player in players]


@router.get("/{player_id}", response_model=PlayerOut)
def get_player(player_id: int, db: Session = Depends(get_db)):
    player = PlayersService.get_by_id(db, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return _to_player_out(db, player)
