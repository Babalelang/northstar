from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, model_validator


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

def _is_goalkeeper_position(position: str | None) -> bool:
    """Matches 'GK', 'Goalkeeper', 'Keeper', case-insensitively."""
    p = (position or "").strip().lower()
    return p == "gk" or "goalkeeper" in p or "keeper" in p


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
    is_captain: bool = False
    goals: int | None = None
    assists: int | None = None
    minutes_played: int | None = None
    # goalkeeper stats
    saves: int | None = None
    clean_sheets: int | None = None
    goals_conceded: int | None = None
    # defender stats
    tackles: int | None = None
    interceptions: int | None = None
    clearances: int | None = None
    form_rating: float | None = None
    market_value_rands: int | None = None  # None = auto-calculate; set a value to override
    overall_rating: float | None = None
    potential_rating: float | None = None

    @model_validator(mode="after")
    def clear_stats_outside_position(self):
        """
        A player's position decides which stat family is allowed:
        - Goalkeepers: saves / clean_sheets / goals_conceded
        - Everyone else: tackles / interceptions / clearances
        Goals, assists, and minutes are always allowed for any position.
        Whichever block doesn't apply gets silently nulled out here, so a
        stray value typed into the wrong field in the admin form never
        makes it into the database.
        """
        if _is_goalkeeper_position(self.playing_position):
            self.tackles = None
            self.interceptions = None
            self.clearances = None
        else:
            self.saves = None
            self.clean_sheets = None
            self.goals_conceded = None
        return self

class PlayerCreate(PlayerBase):
    pass


class PlayerUpdate(PlayerBase):
    pass


class PlayerOut(PlayerBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    team_name: str | None = None
    market_value_rands: int | None = None  # derived for display only, not stored
    created_at: datetime
    updated_at: datetime

# --- Coach schemas live above TeamBase because TeamBase references CoachIn -
# Pydantic resolves annotations at class-definition time, so CoachIn has to
# already exist by the time TeamBase is defined, or this raises a NameError
# at import (this previously sat at the bottom of the file, which broke).
class CoachIn(BaseModel):
    """Nested coach payload sent as part of a team create/update."""
    first_name: str
    last_name: str
    nationality: str | None = None
    date_of_birth: date | None = None
    photo_url: str | None = None
    appointed_date: date | None = None


class CoachOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    nationality: str | None = None
    date_of_birth: date | None = None
    photo_url: str | None = None
    appointed_date: date | None = None


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
    coach: CoachIn | None = None
    average_rating: float | None = None


class TeamCreate(TeamBase):
    pass


class TeamUpdate(TeamBase):
    pass

class CaptainOut(BaseModel):
    """Minimal player payload for showing a team's captain — same idea as CoachOut."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    photo_url: str | None = None
    club_shirt_number: int | None = None
    playing_position: str


class TeamOut(TeamBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    market_value_rands: int | None = None
    coach: CoachOut | None = None
    captain: CaptainOut | None = None  # derived: the player on this team with is_captain=True
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
    top_player_value_rands: int
    top_player_name: str | None = None