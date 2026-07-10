from sqlalchemy import (Column, DateTime,Integer,String, UniqueConstraint, ForeignKey)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.database import Base

class Standing(Base):
    __tablename__ = "standings"

    __table_args__ = (
        UniqueConstraint(
            "season_id",
            "competition_id",
            "team_id",
            name = "uq_standing_team_season_competition",
        ),
    )

    id = Column(Integer, primary_key = True, index = True)

    # originally these were plain strings ("season"/"competition"), but
    # Season.standings and Competition.standings already back_populate
    # against relationship objects here, not raw text - so this now
    # follows the same season_id/competition_id fk pattern used by
    # PlayerStatistic and TeamStatistic
    season_id = Column(Integer, ForeignKey("seasons.id"), nullable = False, index = True)
    season = relationship("Season", back_populates = "standings")

    competition_id = Column(Integer, ForeignKey("competitions.id"), nullable = False, index = True)
    competition = relationship("Competition", back_populates = "standings")

    position = Column(Integer, nullable = False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable = False, index = True)
    team = relationship("Team", back_populates = "standings",)
    played = Column(Integer, nullable = False, default = 0)
    wins = Column(Integer, nullable = False, default = 0)
    losses = Column(Integer, nullable = False, default = 0)
    draws = Column(Integer, nullable = False, default = 0)

    goals_for = Column(Integer, nullable = False, default = 0)
    goals_against = Column(Integer, nullable = False, default = 0)
    goal_difference = Column(Integer, nullable = False, default = 0)

    points = Column(Integer, nullable = False, default = 0)
    form = Column(String(5))

    created_at = Column(DateTime(timezone = True),
                        server_default = func.now(),
                        nullable = False)

    updated_at = Column(DateTime(timezone = True),
                        server_default = func.now(),
                        onupdate = func.now(),
                        nullable = False
                       )
