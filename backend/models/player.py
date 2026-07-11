from sqlalchemy import Column,DateTime,Enum,Date,BigInteger,Integer,String,Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.database import Base
import enum

class PreferredFoot(str, enum.Enum):
    LEFT = "left"
    RIGHT = "right"
    BOTH = "both"
class PlayingPosition(str, enum.Enum):
   GK = "gk"

   CB = "cb"
   LB = "lb"
   RB = "rb"

   CAM = "cam"
   CM = "cm"
   CDM = "cdm"
   LM = "lm"
   RM = "rm"

   LW = "lw"
   RW = "rw"
   CF = "cf"
   ST = "st"
   

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key = True, index = True)

    first_name = Column(String(100),nullable = False, index = True)
    last_name = Column(String(100),nullable = False,index = True)
    date_of_birth = Column(Date, nullable = False)
    nationality = Column(String(64), nullable = False)
    height_cm = Column(Integer, nullable = True)
    preferred_foot = Column(Enum(PreferredFoot),nullable = True)
    photo_url = Column(String, nullable = True)
    club_shirt_number = Column(Integer, nullable = True)
    cty_shirt_number = Column(Integer,nullable = True)
    playing_position = Column(Enum(PlayingPosition), nullable = False)
    goals = Column(Integer, nullable=False, default=0)
    assists = Column(Integer, nullable=False, default=0)
    minutes_played = Column(Integer, nullable=False, default=0)
    form_rating = Column(Float, nullable=True)
    market_value_rands = Column(BigInteger, nullable=True)
    overall_rating = Column(Float, nullable=True)
    potential_rating = Column(Float, nullable=True)
    #relationships
    team_id = Column(Integer,ForeignKey("teams.id"), nullable = False, index = True)
    team = relationship("Team",back_populates = "players")
    player_statistics = relationship("PlayerStatistic",back_populates = "player")
    match_statistics = relationship("MatchStatistic",back_populates="player")
    # foreign_keys pinned to player_id specifically, since MatchEvent also
    # has a second fk to Player (related_player_id, for substitutions)
    match_events = relationship("MatchEvent",back_populates="player", foreign_keys="MatchEvent.player_id")
    
    #audit logs
    created_at = Column(DateTime(timezone = True),
                        server_default = func.now(),
                        nullable = False)
    
    updated_at = Column(DateTime(timezone = True),
                        server_default = func.now(),
                        onupdate = func.now(),
                        nullable = False
                       )
