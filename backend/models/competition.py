from sqlalchemy import(
     Column,
     DateTime,
     Enum,
     Boolean, 
     Integer,
     String, ForeignKey)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.database import Base
import enum

class CompetitionType (str, enum.Enum):
   CUP = "cup"
   LEAGUE = "league"
   INTERNATIONAL = "international"
   WORLD_CUP = "world_cup"

class Competition(Base):
    __tablename__ = "competitions"


    id = Column(Integer, primary_key = True, index = True)

    name = Column(String(100),nullable = False, unique = True, index = True)
    short_name = Column(String(20))
    code = Column(String(25), nullable=False, unique = True, index = True)
    country = Column(String(100),nullable=False,)
    logo_url = Column(String(255))
    governing_body = Column(String(100)) #"PSL"
    tier = Column(Integer)
    is_active = Column(Boolean, default = True, nullable = False)
    competition_type = Column(Enum(CompetitionType),nullable = False, default = CompetitionType.LEAGUE)
    #relationships
    standings = relationship("Standing", back_populates = "competition",cascade="all, delete-orphan")
    seasons = relationship("Season", back_populates = "competition",cascade="all, delete-orphan")
    fixtures = relationship("Fixture", back_populates = "competition",cascade="all, delete-orphan")
    player_statistics = relationship("PlayerStatistic", back_populates = "competition")
    team_statistics = relationship("TeamStatistic",back_populates="competition")

    #audit logs
    created_at = Column(DateTime(timezone = True),
                        server_default = func.now(),
                        nullable = False)
    
    updated_at = Column(DateTime(timezone = True),
                        server_default = func.now(),
                        onupdate = func.now(),
                        nullable = False
                       )
