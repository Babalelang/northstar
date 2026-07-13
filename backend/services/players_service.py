from sqlalchemy.orm import Session

from models.player import Player


class PlayersService:
    """Query helpers for players, shared by the public players API and
    the admin dashboard.
    """

    @staticmethod
    def get_all(db: Session, team_id: int | None = None, position: str | None = None):
        query = db.query(Player)
        if team_id is not None:
            query = query.filter(Player.team_id == team_id)
        if position:
            query = query.filter(Player.playing_position == position)
        return query.order_by(Player.last_name.asc()).all()

    @staticmethod
    def get_by_id(db: Session, player_id: int):
        return db.get(Player, player_id)

    @staticmethod
    def get_captain(db: Session, team_id: int) -> Player | None:
        return (
            db.query(Player)
            .filter(Player.team_id == team_id, Player.is_captain.is_(True))
            .first()
        )

    @staticmethod
    def clear_other_captains(db: Session, team_id: int, keep_player_id: int | None = None):
        """Unset is_captain on every other player at this club so there's
        only ever one captain per team. Call this BEFORE flushing a player
        whose is_captain is being set to True.
        """
        query = db.query(Player).filter(Player.team_id == team_id, Player.is_captain.is_(True))
        if keep_player_id is not None:
            query = query.filter(Player.id != keep_player_id)
        query.update({Player.is_captain: False}, synchronize_session=False)

    @staticmethod
    def create(db: Session, player: Player):
        db.add(player)
        db.commit()
        db.refresh(player)
        return player

    @staticmethod
    def update(db: Session, player: Player):
        db.commit()
        db.refresh(player)
        return player

    @staticmethod
    def delete(db: Session, player: Player):
        db.delete(player)
        db.commit()