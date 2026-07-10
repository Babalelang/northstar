from sqlalchemy import Column,DateTime,Integer,String, ForeignKey,Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.database import Base
import enum


class EventType(str, enum.Enum):
    goal = "goal"
    own_goal = "own_goal"
    penalty = "penalty"
    yellow_card = "yellow_card"
    red_card = "red_card"
    substitution = "substitution"


# this file only had the enum in it, the actual MatchEvent table was
# never written - filling it in so fixtures can have a timeline
# (who scored/was booked/was subbed on, and in which minute)
class MatchEvent(Base):
    __tablename__ = "match_events"

    id = Column(Integer, primary_key = True, index = True)

    fixture_id = Column(Integer, ForeignKey("fixtures.id"), nullable = False, index = True)
    fixture = relationship("Fixture", back_populates = "match_events")

    team_id = Column(Integer, ForeignKey("teams.id"), nullable = False, index = True)
    team = relationship("Team", back_populates = "match_events")

    # player the event happened to (scorer, booked player, player subbed off)
    player_id = Column(Integer, ForeignKey("players.id"), nullable = False, index = True)
    player = relationship("Player", back_populates = "match_events", foreign_keys = [player_id])

    # only used for substitution events - the player coming on
    related_player_id = Column(Integer, ForeignKey("players.id"), nullable = True, index = True)
    related_player = relationship("Player", foreign_keys = [related_player_id])

    event_type = Column(Enum(EventType), nullable = False, index = True)
    minute = Column(Integer, nullable = False)
    extra_minute = Column(Integer, nullable = True)
    detail = Column(String(150), nullable = True)

    #audit logs
    created_at = Column(DateTime(timezone = True),
                        server_default = func.now(),
                        nullable = False)

    updated_at = Column(DateTime(timezone = True),
                        server_default = func.now(),
                        onupdate = func.now(),
                        nullable = False
                       )
