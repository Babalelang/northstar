from sqlalchemy.orm import Session

from models.teams import Team


class TeamsService:
    """Query helpers for teams, shared by the public teams API and
    (indirectly) by the admin dashboard.
    """

    @staticmethod
    def get_all(db: Session, country: str | None = None):
        query = db.query(Team)
        if country:
            query = query.filter(Team.country == country)
        return query.order_by(Team.name.asc()).all()

    @staticmethod
    def get_by_id(db: Session, team_id: int):
        return db.get(Team, team_id)

    @staticmethod
    def create(db: Session, team: Team):
        db.add(team)
        db.commit()
        db.refresh(team)
        return team

    @staticmethod
    def update(db: Session, team: Team):
        db.commit()
        db.refresh(team)
        return team

    @staticmethod
    def delete(db: Session, team: Team):
        db.delete(team)
        db.commit()
