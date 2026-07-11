from sqlalchemy.orm import Session

from models.venue import Venue


class VenuesService:
    """Query helpers for venues. Small table, but fixtures depend on it
    so it gets the same CRUD treatment as everything else.
    """

    @staticmethod
    def get_all(db: Session):
        return db.query(Venue).order_by(Venue.name.asc()).all()

    @staticmethod
    def get_by_id(db: Session, venue_id: int):
        return db.get(Venue, venue_id)

    @staticmethod
    def create(db: Session, venue: Venue):
        db.add(venue)
        db.commit()
        db.refresh(venue)
        return venue

    @staticmethod
    def update(db: Session, venue: Venue):
        db.commit()
        db.refresh(venue)
        return venue

    @staticmethod
    def delete(db: Session, venue: Venue):
        db.delete(venue)
        db.commit()
