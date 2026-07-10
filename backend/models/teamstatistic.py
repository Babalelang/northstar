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


class TeamStatistic(Base):
    __tablename__ = "teamstatistics"

    __table_args__ = (
        UniqueConstraint(
            "team_id",
            "season_id",
            "competition_id",
            name="uq_team_statistics",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    team_id = Column(
        Integer,
        ForeignKey("teams.id"),
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

    # Matches
    matches_played = Column(Integer, nullable=False, default=0)
    wins = Column(Integer, nullable=False, default=0)
    draws = Column(Integer, nullable=False, default=0)
    losses = Column(Integer, nullable=False, default=0)

    # Goals
    goals_for = Column(Integer, nullable=False, default=0)
    goals_against = Column(Integer, nullable=False, default=0)
    goal_difference = Column(Integer, nullable=False, default=0)

    # Points
    points = Column(Integer, nullable=False, default=0)

    # Clean Sheets
    clean_sheets = Column(Integer, nullable=False, default=0)

    # Discipline
    yellow_cards = Column(Integer, nullable=False, default=0)
    red_cards = Column(Integer, nullable=False, default=0)

    # Attack
    shots = Column(Integer, nullable=False, default=0)
    shots_on_target = Column(Integer, nullable=False, default=0)

    # Possession
    possession_percentage = Column(Float, nullable=True)

    # Passing
    passes_attempted = Column(Integer, nullable=False, default=0)
    passes_completed = Column(Integer, nullable=False, default=0)
    pass_accuracy = Column(Float, nullable=True)

    # Advanced Metrics
    expected_goals = Column(Float, nullable=True)
    expected_goals_against = Column(Float, nullable=True)

    # Relationships
    # same fix as MatchStatistic - the other side's attribute is
    # "team_statistics" everywhere, not "teamstatistics"
    team = relationship(
        "Team",
        back_populates="team_statistics",
    )

    season = relationship(
        "Season",
        back_populates="team_statistics",
    )

    competition = relationship(
        "Competition",
        back_populates="team_statistics",
    )

    # Audit logs
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