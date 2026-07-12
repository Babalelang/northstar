from sqlalchemy import Column,DateTime,Integer,BigInteger,String,Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.database import Base

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key = True, index = True)

    name = Column(String(100),nullable = False, unique = True, index = True)
    short_name = Column(String(20))
    city = Column(String(100))
    country = Column(String(100))
    stadium = Column(String(100))
    logo_url = Column(String(255))
    website = Column(String(255))
    founded_year = Column(Integer)
    market_value_rands = Column(BigInteger, nullable=True)
    average_rating = Column(Float, nullable=True)
    
    #relationships
    venue_id = Column(Integer, ForeignKey("venues.id"))
    venue = relationship("Venue", back_populates = "teams") # a venue has many teams
    standings = relationship("Standing", back_populates = "team")
    players = relationship("Player", back_populates = "team")
    home_fixtures = relationship("Fixture", foreign_keys = "Fixture.home_team_id",back_populates = "home_team",)
    away_fixtures = relationship("Fixture", foreign_keys = "Fixture.away_team_id",back_populates = "away_team",)
    match_statistics = relationship("MatchStatistic",back_populates="team")
    team_statistics = relationship("TeamStatistic",back_populates="team")
    match_events = relationship("MatchEvent",back_populates="team")
    coach = relationship("Coach", back_populates="team", uselist=False) 
    #audit logs
    created_at = Column(DateTime(timezone = True),
                        server_default = func.now(),
                        nullable = False)
    
    updated_at = Column(DateTime(timezone = True),
                        server_default = func.now(),
                        onupdate = func.now(),
                        nullable = False
                       )