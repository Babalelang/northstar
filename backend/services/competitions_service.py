from sqlalchemy.orm import Session

from models.competition import Competition


class CompetitionsService:
    """Query helpers for competitions, shared by the public competitions
    API and the admin dashboard.
    """

    @staticmethod
    def get_all(db: Session, is_active: bool | None = None):
        query = db.query(Competition)
        if is_active is not None:
            query = query.filter(Competition.is_active == is_active)
        return query.order_by(Competition.name.asc()).all()

    @staticmethod
    def get_by_id(db: Session, competition_id: int):
        return db.get(Competition, competition_id)

    @staticmethod
    def create(db: Session, competition: Competition):
        db.add(competition)
        db.commit()
        db.refresh(competition)
        return competition

    @staticmethod
    def update(db: Session, competition: Competition):
        db.commit()
        db.refresh(competition)
        return competition

    @staticmethod
    def delete(db: Session, competition: Competition):
        db.delete(competition)
        db.commit()
