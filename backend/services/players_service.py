from sqlalchemy.orm import Session

from models.player import Player
from models.playerstatistic import PlayerStatistic


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

    # -------------------------------------------------------------
    # NEW: season-aware reads. This is what fixes "statistics shows
    # last season's numbers" - it pulls goals/assists/saves/tackles/etc
    # from PlayerStatistic for the requested season instead of the flat
    # (never-reset) columns on Player.
    # -------------------------------------------------------------

    @staticmethod
    def get_all_with_season_stats(
        db: Session,
        season_id: int | None = None,
        competition_id: int | None = None,
        team_id: int | None = None,
        position: str | None = None,
    ):
        """
        Returns a list of (player, stat) tuples where `stat` is the
        matching PlayerStatistic row for the given season (or None if
        the player has no recorded stats for that season yet, or if no
        season_id was passed at all).

        A player with no stat row for the season comes back as
        (player, None) - callers should treat that as zeroed-out stats,
        NOT fall back to the player's flat/career columns, or you're
        right back to the stale-data bug this exists to fix.
        """
        player_query = db.query(Player)
        if team_id is not None:
            player_query = player_query.filter(Player.team_id == team_id)
        if position:
            player_query = player_query.filter(Player.playing_position == position)
        players = player_query.order_by(Player.last_name.asc()).all()

        if season_id is None:
            return [(p, None) for p in players]

        stat_query = db.query(PlayerStatistic).filter(PlayerStatistic.season_id == season_id)
        if competition_id is not None:
            stat_query = stat_query.filter(PlayerStatistic.competition_id == competition_id)
        stats_by_player_id = {s.player_id: s for s in stat_query.all()}

        return [(p, stats_by_player_id.get(p.id)) for p in players]

    @staticmethod
    def get_season_stat(
        db: Session,
        player_id: int,
        season_id: int,
        competition_id: int,
    ) -> PlayerStatistic | None:
        return (
            db.query(PlayerStatistic)
            .filter(
                PlayerStatistic.player_id == player_id,
                PlayerStatistic.season_id == season_id,
                PlayerStatistic.competition_id == competition_id,
            )
            .first()
        )