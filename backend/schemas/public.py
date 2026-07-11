from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class VenueOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    city: str | None = None
    country: str | None = None
    capacity: int | None = None
    image_url: str | None = None


class TeamOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    short_name: str | None = None
    city: str | None = None
    country: str | None = None
    stadium: str | None = None
    logo_url: str | None = None
    website: str | None = None
    founded_year: int | None = None
    market_value_eur: int | None = None
    average_rating: float | None = None


class PlayerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    date_of_birth: date
    nationality: str
    height_cm: int | None = None
    preferred_foot: str | None = None
    photo_url: str | None = None
    club_shirt_number: int | None = None
    playing_position: str
    team_id: int
    team_name: str | None = None
    goals: int = 0
    assists: int = 0
    minutes_played: int = 0
    form_rating: float | None = None
    market_value_eur: int | None = None
    overall_rating: float | None = None
    potential_rating: float | None = None


class CompetitionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    short_name: str | None = None
    code: str
    country: str
    logo_url: str | None = None
    governing_body: str | None = None
    tier: int | None = None
    is_active: bool
    competition_type: str


class SeasonOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    label: str
    start_date: datetime | None = None
    end_date: datetime | None = None
    is_current: bool
    competition_id: int


class FixtureTeamOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    short_name: str | None = None
    logo_url: str | None = None


class FixtureOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    home_score: int
    away_score: int
    match_datetime: datetime
    status: str
    matchweek: int | None = None
    round_name: str | None = None
    referee: str | None = None
    attendance: int | None = None
    home_team: FixtureTeamOut
    away_team: FixtureTeamOut
    venue_name: str | None = None
    season_id: int
    competition_id: int
