from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.database import Base


class Coach(Base):
    __tablename__ = "coaches"

    id = Column(Integer, primary_key=True, index=True)

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    nationality = Column(String(100))
    date_of_birth = Column(Date, nullable=True)
    photo_url = Column(String(255), nullable=True)
    appointed_date = Column(Date, nullable=True)

    # one coach currently at one club - unique enforces a club can't end up
    # with two "current" coach rows attached to it at the same time
    team_id = Column(Integer, ForeignKey("teams.id"), unique=True, nullable=True)
    team = relationship("Team", back_populates="coach")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)