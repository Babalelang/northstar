from sqlalchemy import Column,DateTime,Integer,String, ForeignKey,Enum, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.database import Base
import enum

class FixtureStatus (str, enum.Enum):
    SCHEDULED = "scheduled"
    LIVE = "live"
    FULLTIME = "fulltime"
    HALFTIME = "halftime"
    POSTPONED = "postponed"
    CANCELLED = "cancelled"
    
class Fixture(Base):
    __tablename__ = "fixtures"
    __table_args__ = (
        CheckConstraint(
            "home_team_id != away_team_id",
             name = "check_different_teams",
        ),
        UniqueConstraint(
            "season_id",
            "competition_id",
            "match_datetime",
            "home_team_id",
            "away_team_id",
            name = "uq_fixture",
        ),
    )

    id = Column(Integer, primary_key = True, index = True)
    home_score = Column(Integer, nullable = False, default = 0)
    away_score = Column(Integer, nullable = False, default = 0)
    match_datetime = Column(DateTime(timezone = True), nullable = False, index = True)
    status = Column(Enum(FixtureStatus),nullable = False, default = FixtureStatus.SCHEDULED)
    matchweek = Column(Integer)
    round_name = Column(String(50))
    referee = Column(String(100), nullable=True)
    attendance = Column(Integer, nullable=True)

    #relationships
    # index=0 evaluates to index=False, which silently drops the index -
    # these are fk columns we filter/join on constantly, so they need index=True
    home_team_id = Column(Integer,ForeignKey("teams.id"), nullable = False, index = True)
    away_team_id = Column(Integer,ForeignKey("teams.id"), nullable = False, index = True)
    home_team = relationship("Team",foreign_keys = [home_team_id], back_populates = "home_fixtures")
    away_team = relationship("Team",foreign_keys = [away_team_id],back_populates = "away_fixtures")
    venue_id = Column(Integer,ForeignKey("venues.id"), nullable = False, index = True)
    venue = relationship("Venue", back_populates = "fixtures",)
    season_id = Column(Integer,ForeignKey("seasons.id"), nullable = False,index = True)
    season = relationship("Season", back_populates = "fixtures",)
    competition_id = Column(Integer,ForeignKey("competitions.id"), nullable = False,index = True)
    competition = relationship("Competition", back_populates = "fixtures")
    match_statistics = relationship("MatchStatistic",back_populates="fixture")
    match_events = relationship("MatchEvent",back_populates="fixture")
    
    #audit logs
    created_at = Column(DateTime(timezone = True),
                        server_default = func.now(),
                        nullable = False)
    
    updated_at = Column(DateTime(timezone = True),
                        server_default = func.now(),
                        onupdate = func.now(),
                        nullable = False
                       )
