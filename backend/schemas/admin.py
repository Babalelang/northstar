from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class AnnouncementBase(BaseModel):
    title: str
    summary: str | None = None
    body: str
    status: str = "draft"
    announcement_type: str = "general"
    is_pinned: bool = False
    featured_image_url: str | None = None


class AnnouncementCreate(AnnouncementBase):
    slug: str | None = None


class AnnouncementUpdate(AnnouncementBase):
    slug: str | None = None


class AnnouncementOut(AnnouncementBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    author_id: int
    published_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class PlayerBase(BaseModel):
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
    goals: int | None = None
    assists: int | None = None
    minutes_played: int | None = None
    form_rating: float | None = None
    market_value_rands: int | None = None  # None = auto-calculate; set a value to override
    overall_rating: float | None = None
    potential_rating: float | None = None


class PlayerCreate(PlayerBase):
    pass


class PlayerUpdate(PlayerBase):
    pass


class PlayerOut(PlayerBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    team_name: str | None = None
    market_value_eur: int | None = None  # derived for display only, not stored
    created_at: datetime
    updated_at: datetime


class PlayerOut(PlayerBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    team_name: str | None = None
    created_at: datetime
    updated_at: datetime


class TeamBase(BaseModel):
    name: str
    short_name: str | None = None
    city: str | None = None
    country: str | None = None
    stadium: str | None = None
    logo_url: str | None = None
    website: str | None = None
    founded_year: int | None = None
    market_value_rands: int | None = None
    average_rating: float | None = None


class TeamCreate(TeamBase):
    pass


class TeamUpdate(TeamBase):
    pass


class TeamOut(TeamBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    market_value_eur: int | None = None  # derived for display only, not stored
    created_at: datetime
    updated_at: datetime

class CompetitionBase(BaseModel):
    name: str
    short_name: str | None = None
    code: str
    country: str
    logo_url: str | None = None
    governing_body: str | None = None
    tier: int | None = None
    is_active: bool = True
    competition_type: str = "league"


class CompetitionCreate(CompetitionBase):
    pass


class CompetitionUpdate(CompetitionBase):
    pass


class CompetitionOut(CompetitionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class SeasonBase(BaseModel):
    label: str
    start_date: datetime | None = None
    end_date: datetime | None = None
    is_current: bool = False
    competition_id: int


class SeasonCreate(SeasonBase):
    pass


class SeasonUpdate(SeasonBase):
    pass


class SeasonOut(SeasonBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class StandingBase(BaseModel):
    position: int
    played: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    goals_for: int = 0
    goals_against: int = 0
    goal_difference: int = 0
    points: int = 0
    form: str | None = None
    season_id: int
    competition_id: int
    team_id: int


class StandingCreate(StandingBase):
    pass


class StandingUpdate(StandingBase):
    pass


class StandingOut(StandingBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    team_name: str | None = None
    season_label: str | None = None
    competition_name: str | None = None
    created_at: datetime
    updated_at: datetime


class VenueBase(BaseModel):
    name: str
    city: str | None = None
    country: str | None = None
    capacity: int | None = None
    address: str | None = None
    surface: str | None = None
    image_url: str | None = None


class VenueCreate(VenueBase):
    pass


class VenueUpdate(VenueBase):
    pass


class VenueOut(VenueBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class FixtureBase(BaseModel):
    home_score: int = 0
    away_score: int = 0
    match_datetime: datetime
    status: str = "scheduled"
    matchweek: int | None = None
    round_name: str | None = None
    referee: str | None = None
    attendance: int | None = None
    home_team_id: int
    away_team_id: int
    venue_id: int
    season_id: int
    competition_id: int


class FixtureCreate(FixtureBase):
    pass


class FixtureUpdate(FixtureBase):
    pass


class FixtureOut(FixtureBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    home_team_name: str | None = None
    away_team_name: str | None = None
    venue_name: str | None = None
    season_label: str | None = None
    competition_name: str | None = None
    created_at: datetime
    updated_at: datetime


class DashboardSummary(BaseModel):
    total_players: int
    total_teams: int
    total_announcements: int
    total_competitions: int
    total_seasons: int
    total_standings: int
    total_fixtures: int
    total_venues: int
    average_player_rating: float
    top_player_value_eur: int
    top_player_name: str | None = None
