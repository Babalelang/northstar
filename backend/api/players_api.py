from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.database import get_db
from models import Team
from schemas.public import PlayerOut
from services.players_service import PlayersService

router = APIRouter(prefix="/players", tags=["Players"])


def _to_player_out(db: Session, player, stat=None, season_requested: bool = False) -> PlayerOut:
    team = db.get(Team, player.team_id)
    item = PlayerOut.model_validate(player)
    item.team_name = team.name if team else None

    if season_requested:
        # No PlayerStatistic row for this player in the requested season
        # -> zero everything out. Falling back to player.goals etc here
        # would just reintroduce the "shows last season's stats" bug.
        item.goals = stat.goals if stat else 0
        item.assists = stat.assists if stat else 0
        item.minutes_played = stat.minutes_played if stat else 0
        item.saves = stat.saves if stat else None
        item.clean_sheets = stat.clean_sheets if stat else None
        item.goals_conceded = stat.goals_conceded if stat else None
        item.tackles = stat.tackles if stat else None
        item.interceptions = stat.interceptions if stat else None
        item.clearances = stat.clearances if stat else None

    return item


@router.get("/", response_model=list[PlayerOut])
def list_players(
    team_id: int | None = None,
    position: str | None = None,
    season_id: int | None = None,
    competition_id: int | None = None,
    db: Session = Depends(get_db),
):
    """Every player in our own database, optionally filtered by team or
    playing position - this is what the players/market/statistics pages
    render from, no outside source involved.

    Pass season_id (and, if a player could belong to more than one
    competition, competition_id) to get that season's goals/assists/
    saves/tackles/etc instead of the player's flat, never-reset totals.
    Omit season_id to keep the old behaviour.
    """
    if season_id is not None:
        pairs = PlayersService.get_all_with_season_stats(
            db, season_id=season_id, competition_id=competition_id, team_id=team_id, position=position
        )
        return [_to_player_out(db, player, stat, season_requested=True) for player, stat in pairs]

    players = PlayersService.get_all(db, team_id=team_id, position=position)
    return [_to_player_out(db, player) for player in players]


@router.get("/{player_id}", response_model=PlayerOut)
def get_player(
    player_id: int,
    season_id: int | None = None,
    competition_id: int | None = None,
    db: Session = Depends(get_db),
):
    player = PlayersService.get_by_id(db, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    if season_id is not None and competition_id is not None:
        stat = PlayersService.get_season_stat(db, player_id, season_id, competition_id)
        return _to_player_out(db, player, stat, season_requested=True)

    return _to_player_out(db, player)