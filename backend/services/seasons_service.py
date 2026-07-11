from sqlalchemy.orm import Session

from models.season import Season


class SeasonsService:
    """Query helpers for seasons, shared by the public seasons API and
    the admin dashboard.
    """

    @staticmethod
    def get_all(db: Session, competition_id: int | None = None):
        query = db.query(Season)
        if competition_id is not None:
            query = query.filter(Season.competition_id == competition_id)
        return query.order_by(Season.label.desc()).all()

    @staticmethod
    def get_current(db: Session, competition_id: int | None = None):
        query = db.query(Season).filter(Season.is_current == True)  # noqa: E712
        if competition_id is not None:
            query = query.filter(Season.competition_id == competition_id)
        return query.first()

    @staticmethod
    def get_by_id(db: Session, season_id: int):
        return db.get(Season, season_id)

    @staticmethod
    def create(db: Session, season: Season):
        db.add(season)
        db.commit()
        db.refresh(season)
        return season

    @staticmethod
    def update(db: Session, season: Season):
        db.commit()
        db.refresh(season)
        return season

    @staticmethod
    def delete(db: Session, season: Season):
        db.delete(season)
        db.commit()
