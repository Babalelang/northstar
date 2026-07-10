from sqlalchemy import Column,DateTime,Enum,Date,Float,Integer,String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.database import Base
import enum
   

class PlayerStatistic(Base):
    __tablename__ = "playerstatistics"
    __table_args__ = (
        UniqueConstraint(
            "player_id",
            "season_id",
            "competition_id",
            name="uq_player_statistics",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    player_id = Column(
        Integer,
        ForeignKey("players.id"),
        nullable=False,
        index=True,
    )

    season_id = Column(
        Integer,
        ForeignKey("seasons.id"),
        nullable=False,
        index=True,
    )

    competition_id = Column(
        Integer,
        ForeignKey("competitions.id"),
        nullable=False,
        index=True,
    )

    appearances = Column(Integer, nullable=False, default=0)

    starts = Column(Integer, nullable=False, default=0)

    minutes_played = Column(Integer, nullable=False, default=0)

    goals = Column(Integer, nullable=False, default=0)

    assists = Column(Integer, nullable=False, default=0)

    yellow_cards = Column(Integer, nullable=False, default=0)

    red_cards = Column(Integer, nullable=False, default=0)

    clean_sheets = Column(Integer, nullable=False, default=0)

    own_goals = Column(Integer, nullable=False, default=0)

    penalties_scored = Column(Integer, nullable=False, default=0)

    penalties_missed = Column(Integer, nullable=False, default=0)

    rating = Column(Float, nullable=True)

    player = relationship(
        "Player",
        back_populates="player_statistics",
    )

    season = relationship(
        "Season",
        back_populates="player_statistics",
    )

    competition = relationship(
        "Competition",
        back_populates="player_statistics",
    )
    #audit logs
    created_at = Column(DateTime(timezone = True),
                        server_default = func.now(),
                        nullable = False)
    
    updated_at = Column(DateTime(timezone = True),
                        server_default = func.now(),
                        onupdate = func.now(),
                        nullable = False
                       )
