from sqlalchemy import (
    Column,
    Integer,
    Float,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.database import Base


class MatchStatistic(Base):
    __tablename__ = "matchstatistics"

    __table_args__ = (
        UniqueConstraint(
            "fixture_id",
            "player_id",
            name="uq_match_player",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    # Foreign Keys
    fixture_id = Column(
        Integer,
        ForeignKey("fixtures.id"),
        nullable=False,
        index=True,
    )

    player_id = Column(
        Integer,
        ForeignKey("players.id"),
        nullable=False,
        index=True,
    )

    team_id = Column(
        Integer,
        ForeignKey("teams.id"),
        nullable=False,
        index=True,
    )

    # Playing Time
    started = Column(Integer, nullable=False, default=0)
    minutes_played = Column(Integer, nullable=False, default=0)

    # Attacking
    goals = Column(Integer, nullable=False, default=0)
    assists = Column(Integer, nullable=False, default=0)
    shots = Column(Integer, nullable=False, default=0)
    shots_on_target = Column(Integer, nullable=False, default=0)

    # Passing
    passes_attempted = Column(Integer, nullable=False, default=0)
    passes_completed = Column(Integer, nullable=False, default=0)
    key_passes = Column(Integer, nullable=False, default=0)

    # Dribbling
    dribbles_attempted = Column(Integer, nullable=False, default=0)
    dribbles_completed = Column(Integer, nullable=False, default=0)

    # Defensive
    tackles = Column(Integer, nullable=False, default=0)
    interceptions = Column(Integer, nullable=False, default=0)
    clearances = Column(Integer, nullable=False, default=0)
    blocks = Column(Integer, nullable=False, default=0)

    # Goalkeeping
    saves = Column(Integer, nullable=False, default=0)
    clean_sheet = Column(Integer, nullable=False, default=0)

    # Discipline
    fouls_committed = Column(Integer, nullable=False, default=0)
    fouls_won = Column(Integer, nullable=False, default=0)
    yellow_cards = Column(Integer, nullable=False, default=0)
    red_cards = Column(Integer, nullable=False, default=0)

    # Advanced
    xg = Column(Float, nullable=True)
    xa = Column(Float, nullable=True)

    rating = Column(Float, nullable=True)

    # Relationships
    # back_populates has to name the attribute on the OTHER side exactly -
    # Player/Fixture/Team all call it "match_statistics" (snake_case),
    # this was pointing at "matchstatistics" which doesn't exist on any of them
    player = relationship(
        "Player",
        back_populates="match_statistics",
    )

    fixture = relationship(
        "Fixture",
        back_populates="match_statistics",
    )

    team = relationship(
        "Team",
        back_populates="match_statistics",
    )

    # Audit
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )