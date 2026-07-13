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


# Minimal nested shapes for the season/competition each standing belongs to.
# These were missing entirely before, which is why the frontend's season
# filter showed "undefined" - Standing.season_id/competition_id are real
# columns on the model, but StandingOut never exposed them (or the related
# Season/Competition objects) to the API response at all.
class SeasonOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    label: str


class CompetitionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


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
    season: SeasonOut
    competition: CompetitionOut
    updated_at: datetime


class SyncResponse(BaseModel):
    synced: int
    message: str