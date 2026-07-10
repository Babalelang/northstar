from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TeamOut(BaseModel):
    # from_attributes lets pydantic read straight off the sqlalchemy
    # model's attributes instead of requiring a dict
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    short_name: str | None = None
    logo_url: str | None = None


class StandingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    position: int
    played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    goal_difference: int
    points: int
    form: str | None = None
    team: TeamOut
    updated_at: datetime


class SyncResponse(BaseModel):
    synced: int
    message: str
