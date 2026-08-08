import re
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.database import get_db
from api.deps import get_current_user
from models import (
    Announcement,
    AnnouncementStatus,
    AnnouncementType,
    Competition,
    Fixture,
    FixtureStatus,
    Player,
    Season,
    Standing,
    Team,
    Venue,
    Coach,

)
from models.playerstatistic import PlayerStatistic
from models.user import User
from schemas.admin import (
    AnnouncementCreate,
    AnnouncementOut,
    AnnouncementUpdate,
    CompetitionCreate,
    CompetitionOut,
    CompetitionUpdate,
    DashboardSummary,
    FixtureCreate,
    FixtureOut,
    FixtureUpdate,
    PlayerCreate,
    PlayerOut,
    PlayerUpdate,
    PlayerStatisticCreate,
    PlayerStatisticOut,
    PlayerStatisticUpdate,
    SeasonCreate,
    SeasonOut,
    SeasonUpdate,
    StandingCreate,
    StandingOut,
    StandingUpdate,
    TeamCreate,
    TeamOut,
    TeamUpdate,
    VenueCreate,
    VenueOut,
    VenueUpdate,
    CaptainOut,
)
from services.analytics_service import apply_player_metrics
from services.players_service import PlayersService

router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(get_current_user)])


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "item"


@router.get("/overview", response_model=DashboardSummary)
def dashboard_overview(db: Session = Depends(get_db)):
    players = db.query(Player).all()
    teams = db.query(Team).all()
    announcements = db.query(Announcement).all()
    competitions = db.query(Competition).all()
    seasons = db.query(Season).all()
    standings = db.query(Standing).all()
    fixtures = db.query(Fixture).all()
    venues = db.query(Venue).all()

    average_player_rating = round(
        sum(float(player.overall_rating or 0) for player in players) / len(players), 1
    ) if players else 0.0

    top_player = max(players, key=lambda player: player.market_value_rands or 0, default=None)
    return DashboardSummary(
        total_players=len(players),
        total_teams=len(teams),
        total_announcements=len(announcements),
        total_competitions=len(competitions),
        total_seasons=len(seasons),
        total_standings=len(standings),
        total_fixtures=len(fixtures),
        total_venues=len(venues),
        average_player_rating=average_player_rating,
        top_player_value_rands=top_player.market_value_rands or 0 if top_player else 0,
        top_player_name=(f"{top_player.first_name} {top_player.last_name}" if top_player else None),
    )


@router.get("/announcements", response_model=list[AnnouncementOut])
def list_announcements(db: Session = Depends(get_db)):
    return (
        db.query(Announcement)
        .order_by(Announcement.created_at.desc())
        .all()
    )


@router.post("/announcements", response_model=AnnouncementOut, status_code=status.HTTP_201_CREATED)
def create_announcement(payload: AnnouncementCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    slug = payload.slug or _slugify(payload.title)
    item = Announcement(
        title=payload.title,
        slug=slug,
        summary=payload.summary,
        body=payload.body,
        status=AnnouncementStatus(payload.status),
        announcement_type=AnnouncementType(payload.announcement_type),
        is_pinned=payload.is_pinned,
        featured_image_url=payload.featured_image_url,
        author_id=current_user.id,
        published_at=datetime.utcnow() if payload.status == "published" else None,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/announcements/{announcement_id}", response_model=AnnouncementOut)
def update_announcement(announcement_id: int, payload: AnnouncementUpdate, db: Session = Depends(get_db)):
    item = db.get(Announcement, announcement_id)
    if not item:
        raise HTTPException(status_code=404, detail="Announcement not found")

    item.title = payload.title
    item.slug = payload.slug or _slugify(payload.title)
    item.summary = payload.summary
    item.body = payload.body
    item.status = AnnouncementStatus(payload.status)
    item.announcement_type = AnnouncementType(payload.announcement_type)
    item.is_pinned = payload.is_pinned
    item.featured_image_url = payload.featured_image_url
    item.published_at = datetime.utcnow() if payload.status == "published" else None
    db.commit()
    db.refresh(item)
    return item


@router.delete("/announcements/{announcement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_announcement(announcement_id: int, db: Session = Depends(get_db)):
    item = db.get(Announcement, announcement_id)
    if not item:
        raise HTTPException(status_code=404, detail="Announcement not found")
    db.delete(item)
    db.commit()
    return None


@router.get("/players", response_model=list[PlayerOut])
def list_players(db: Session = Depends(get_db)):
    players = db.query(Player).order_by(Player.created_at.desc()).all()

    output = []

    for player in players:
        team = db.get(Team, player.team_id)

        item = PlayerOut.model_validate(player)
        item.team_name = team.name if team else None
        item.market_value_rands = player.market_value_rands

        output.append(item)

    return output


@router.post("/players", response_model=PlayerOut, status_code=status.HTTP_201_CREATED)
def create_player(payload: PlayerCreate, db: Session = Depends(get_db)):
    item = Player(
        first_name=payload.first_name,
        last_name=payload.last_name,
        date_of_birth=payload.date_of_birth,
        nationality=payload.nationality,
        height_cm=payload.height_cm,
        preferred_foot=payload.preferred_foot,
        photo_url=payload.photo_url,
        club_shirt_number=payload.club_shirt_number,
        playing_position=payload.playing_position,
        team_id=payload.team_id,
        is_captain=payload.is_captain,
        goals=payload.goals or 0,
        assists=payload.assists or 0,
        minutes_played=payload.minutes_played or 0,
        saves=payload.saves,
        clean_sheets=payload.clean_sheets,
        goals_conceded=payload.goals_conceded,
        tackles=payload.tackles,
        interceptions=payload.interceptions,
        clearances=payload.clearances,
        form_rating=payload.form_rating,
    )
    apply_player_metrics(
    item,
    override_rands=payload.market_value_rands,
    override_overall=payload.overall_rating,
    override_potential=payload.potential_rating,
)
    db.add(item)
    db.flush()  # get item.id before touching captain exclusivity

    if payload.is_captain:
        PlayersService.clear_other_captains(db, team_id=item.team_id, keep_player_id=item.id)

    db.commit()
    db.refresh(item)
    out = PlayerOut.model_validate(item)
    out.market_value_rands = item.market_value_rands
    return out


@router.put("/players/{player_id}", response_model=PlayerOut)
def update_player(player_id: int, payload: PlayerUpdate, db: Session = Depends(get_db)):
    item = db.get(Player, player_id)
    if not item:
        raise HTTPException(status_code=404, detail="Player not found")

    item.first_name = payload.first_name
    item.last_name = payload.last_name
    item.date_of_birth = payload.date_of_birth
    item.nationality = payload.nationality
    item.height_cm = payload.height_cm
    item.preferred_foot = payload.preferred_foot
    item.photo_url = payload.photo_url
    item.club_shirt_number = payload.club_shirt_number
    item.playing_position = payload.playing_position
    item.team_id = payload.team_id
    item.is_captain = payload.is_captain
    item.goals = payload.goals or 0
    item.assists = payload.assists or 0
    item.minutes_played = payload.minutes_played or 0
    item.saves = payload.saves
    item.clean_sheets = payload.clean_sheets
    item.goals_conceded = payload.goals_conceded
    item.tackles = payload.tackles
    item.interceptions = payload.interceptions
    item.clearances = payload.clearances
    item.form_rating = payload.form_rating
    apply_player_metrics(
    item,
    override_rands=payload.market_value_rands,
    override_overall=payload.overall_rating,
    override_potential=payload.potential_rating,
)

    if payload.is_captain:
        PlayersService.clear_other_captains(db, team_id=item.team_id, keep_player_id=item.id)

    db.commit()
    db.refresh(item)
    out = PlayerOut.model_validate(item)
    out.market_value_rands = item.market_value_rands
    return out


# ---------------------------------------------------------------------
# NEW: PlayerStatistic CRUD - season-scoped goals/assists/saves/tackles/
# etc, kept separate from the flat fields on Player above. This is what
# the admin Players form's new "Statistics season" selector reads from
# and writes to, so entering this season's numbers no longer overwrites
# (or gets overwritten by) last season's.
# ---------------------------------------------------------------------

def _player_statistic_out(db: Session, item: PlayerStatistic) -> PlayerStatisticOut:
    player = db.get(Player, item.player_id)
    season = db.get(Season, item.season_id)
    competition = db.get(Competition, item.competition_id)
    out = PlayerStatisticOut.model_validate(item)
    out.player_name = f"{player.first_name} {player.last_name}" if player else None
    out.season_label = season.label if season else None
    out.competition_name = competition.name if competition else None
    return out


@router.get("/player-statistics", response_model=list[PlayerStatisticOut])
def list_player_statistics(
    player_id: int | None = None,
    season_id: int | None = None,
    competition_id: int | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(PlayerStatistic)
    if player_id is not None:
        query = query.filter(PlayerStatistic.player_id == player_id)
    if season_id is not None:
        query = query.filter(PlayerStatistic.season_id == season_id)
    if competition_id is not None:
        query = query.filter(PlayerStatistic.competition_id == competition_id)
    items = query.all()
    return [_player_statistic_out(db, item) for item in items]


@router.post("/player-statistics", response_model=PlayerStatisticOut, status_code=status.HTTP_201_CREATED)
def create_player_statistic(payload: PlayerStatisticCreate, db: Session = Depends(get_db)):
    dupe = (
        db.query(PlayerStatistic)
        .filter(
            PlayerStatistic.player_id == payload.player_id,
            PlayerStatistic.season_id == payload.season_id,
            PlayerStatistic.competition_id == payload.competition_id,
        )
        .first()
    )
    if dupe:
        raise HTTPException(
            status_code=409,
            detail="A stats row for this player/season/competition already exists - update it instead.",
        )

    item = PlayerStatistic(
        player_id=payload.player_id,
        season_id=payload.season_id,
        competition_id=payload.competition_id,
        appearances=payload.appearances,
        starts=payload.starts,
        minutes_played=payload.minutes_played,
        goals=payload.goals,
        assists=payload.assists,
        yellow_cards=payload.yellow_cards,
        red_cards=payload.red_cards,
        own_goals=payload.own_goals,
        penalties_scored=payload.penalties_scored,
        penalties_missed=payload.penalties_missed,
        rating=payload.rating,
        saves=payload.saves,
        goals_conceded=payload.goals_conceded,
        clean_sheets=payload.clean_sheets,
        tackles=payload.tackles,
        interceptions=payload.interceptions,
        clearances=payload.clearances,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return _player_statistic_out(db, item)


@router.put("/player-statistics/{stat_id}", response_model=PlayerStatisticOut)
def update_player_statistic(stat_id: int, payload: PlayerStatisticUpdate, db: Session = Depends(get_db)):
    item = db.get(PlayerStatistic, stat_id)
    if not item:
        raise HTTPException(status_code=404, detail="Player statistic not found")

    item.player_id = payload.player_id
    item.season_id = payload.season_id
    item.competition_id = payload.competition_id
    item.appearances = payload.appearances
    item.starts = payload.starts
    item.minutes_played = payload.minutes_played
    item.goals = payload.goals
    item.assists = payload.assists
    item.yellow_cards = payload.yellow_cards
    item.red_cards = payload.red_cards
    item.own_goals = payload.own_goals
    item.penalties_scored = payload.penalties_scored
    item.penalties_missed = payload.penalties_missed
    item.rating = payload.rating
    item.saves = payload.saves
    item.goals_conceded = payload.goals_conceded
    item.clean_sheets = payload.clean_sheets
    item.tackles = payload.tackles
    item.interceptions = payload.interceptions
    item.clearances = payload.clearances

    db.commit()
    db.refresh(item)
    return _player_statistic_out(db, item)


@router.delete("/player-statistics/{stat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_player_statistic(stat_id: int, db: Session = Depends(get_db)):
    item = db.get(PlayerStatistic, stat_id)
    if not item:
        raise HTTPException(status_code=404, detail="Player statistic not found")
    db.delete(item)
    db.commit()
    return None


@router.get("/teams", response_model=list[TeamOut])
def list_teams(db: Session = Depends(get_db)):
    teams = db.query(Team).order_by(Team.name.asc()).all()

    output = []
    for team in teams:
        item = TeamOut.model_validate(team)
        item.market_value_rands = team.market_value_rands
        captain = PlayersService.get_captain(db, team.id)
        item.captain = CaptainOut.model_validate(captain) if captain else None
        output.append(item)

    return output

@router.post("/teams", response_model=TeamOut, status_code=status.HTTP_201_CREATED)
def create_team(payload: TeamCreate, db: Session = Depends(get_db)):
    item = Team(
        name=payload.name,
        short_name=payload.short_name,
        city=payload.city,
        country=payload.country,
        stadium=payload.stadium,
        logo_url=payload.logo_url,
        website=payload.website,
        founded_year=payload.founded_year,
        market_value_rands=payload.market_value_rands or 0,
        average_rating=payload.average_rating,
    )
    db.add(item)
    db.flush()  # assigns item.id before we attach the coach row

    if payload.coach:
        item.coach = Coach(
            first_name=payload.coach.first_name,
            last_name=payload.coach.last_name,
            nationality=payload.coach.nationality,
            date_of_birth=payload.coach.date_of_birth,
            photo_url=payload.coach.photo_url,
            appointed_date=payload.coach.appointed_date,
        )

    db.commit()
    db.refresh(item)
    out = TeamOut.model_validate(item)
    out.market_value_rands = item.market_value_rands
    return out


@router.put("/teams/{team_id}", response_model=TeamOut)
def update_team(team_id: int, payload: TeamUpdate, db: Session = Depends(get_db)):
    item = db.get(Team, team_id)
    if not item:
        raise HTTPException(status_code=404, detail="Team not found")

    item.name = payload.name
    item.short_name = payload.short_name
    item.city = payload.city
    item.country = payload.country
    item.stadium = payload.stadium
    item.logo_url = payload.logo_url
    item.website = payload.website
    item.founded_year = payload.founded_year
    item.market_value_rands = payload.market_value_rands or 0
    item.average_rating = payload.average_rating

    # blank/omitted coach = leave whoever's already there - same convention
    # as leaving the password field blank on a user update
    if payload.coach:
        if item.coach:
            item.coach.first_name = payload.coach.first_name
            item.coach.last_name = payload.coach.last_name
            item.coach.nationality = payload.coach.nationality
            item.coach.date_of_birth = payload.coach.date_of_birth
            item.coach.photo_url = payload.coach.photo_url
            item.coach.appointed_date = payload.coach.appointed_date
        else:
            item.coach = Coach(
                first_name=payload.coach.first_name,
                last_name=payload.coach.last_name,
                nationality=payload.coach.nationality,
                date_of_birth=payload.coach.date_of_birth,
                photo_url=payload.coach.photo_url,
                appointed_date=payload.coach.appointed_date,
            )

    db.commit()
    db.refresh(item)
    out = TeamOut.model_validate(item)
    out.market_value_rands = item.market_value_rands
    return out

@router.get("/competitions", response_model=list[CompetitionOut])
def list_competitions(db: Session = Depends(get_db)):
    return db.query(Competition).order_by(Competition.name.asc()).all()


@router.post("/competitions", response_model=CompetitionOut, status_code=status.HTTP_201_CREATED)
def create_competition(payload: CompetitionCreate, db: Session = Depends(get_db)):
    item = Competition(
        name=payload.name,
        short_name=payload.short_name,
        code=payload.code,
        country=payload.country,
        logo_url=payload.logo_url,
        governing_body=payload.governing_body,
        tier=payload.tier,
        is_active=payload.is_active,
        competition_type=payload.competition_type,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/competitions/{competition_id}", response_model=CompetitionOut)
def update_competition(competition_id: int, payload: CompetitionUpdate, db: Session = Depends(get_db)):
    item = db.get(Competition, competition_id)
    if not item:
        raise HTTPException(status_code=404, detail="Competition not found")
    item.name = payload.name
    item.short_name = payload.short_name
    item.code = payload.code
    item.country = payload.country
    item.logo_url = payload.logo_url
    item.governing_body = payload.governing_body
    item.tier = payload.tier
    item.is_active = payload.is_active
    item.competition_type = payload.competition_type
    db.commit()
    db.refresh(item)
    return item


@router.delete("/competitions/{competition_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_competition(competition_id: int, db: Session = Depends(get_db)):
    item = db.get(Competition, competition_id)
    if not item:
        raise HTTPException(status_code=404, detail="Competition not found")
    db.delete(item)
    db.commit()
    return None


@router.get("/seasons", response_model=list[SeasonOut])
def list_seasons(db: Session = Depends(get_db)):
    return db.query(Season).order_by(Season.label.asc()).all()


@router.post("/seasons", response_model=SeasonOut, status_code=status.HTTP_201_CREATED)
def create_season(payload: SeasonCreate, db: Session = Depends(get_db)):
    item = Season(
        label=payload.label,
        start_date=payload.start_date,
        end_date=payload.end_date,
        is_current=payload.is_current,
        competition_id=payload.competition_id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/seasons/{season_id}", response_model=SeasonOut)
def update_season(season_id: int, payload: SeasonUpdate, db: Session = Depends(get_db)):
    item = db.get(Season, season_id)
    if not item:
        raise HTTPException(status_code=404, detail="Season not found")
    item.label = payload.label
    item.start_date = payload.start_date
    item.end_date = payload.end_date
    item.is_current = payload.is_current
    item.competition_id = payload.competition_id
    db.commit()
    db.refresh(item)
    return item


@router.delete("/seasons/{season_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_season(season_id: int, db: Session = Depends(get_db)):
    item = db.get(Season, season_id)
    if not item:
        raise HTTPException(status_code=404, detail="Season not found")
    db.delete(item)
    db.commit()
    return None


@router.get("/standings", response_model=list[StandingOut])
def list_standings(db: Session = Depends(get_db)):
    standings = db.query(Standing).order_by(Standing.position.asc()).all()
    output = []
    for standing in standings:
        season = db.get(Season, standing.season_id)
        competition = db.get(Competition, standing.competition_id)
        team = db.get(Team, standing.team_id)
        item = StandingOut.model_validate(standing)
        item.team_name = team.name if team else None
        item.season_label = season.label if season else None
        item.competition_name = competition.name if competition else None
        output.append(item)
    return output


@router.post("/standings", response_model=StandingOut, status_code=status.HTTP_201_CREATED)
def create_standing(payload: StandingCreate, db: Session = Depends(get_db)):
    item = Standing(
        position=payload.position,
        played=payload.played,
        wins=payload.wins,
        draws=payload.draws,
        losses=payload.losses,
        goals_for=payload.goals_for,
        goals_against=payload.goals_against,
        goal_difference=payload.goal_difference,
        points=payload.points,
        form=payload.form,
        season_id=payload.season_id,
        competition_id=payload.competition_id,
        team_id=payload.team_id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return StandingOut.model_validate(item)


@router.put("/standings/{standing_id}", response_model=StandingOut)
def update_standing(standing_id: int, payload: StandingUpdate, db: Session = Depends(get_db)):
    item = db.get(Standing, standing_id)
    if not item:
        raise HTTPException(status_code=404, detail="Standing not found")
    item.position = payload.position
    item.played = payload.played
    item.wins = payload.wins
    item.draws = payload.draws
    item.losses = payload.losses
    item.goals_for = payload.goals_for
    item.goals_against = payload.goals_against
    item.goal_difference = payload.goal_difference
    item.points = payload.points
    item.form = payload.form
    item.season_id = payload.season_id
    item.competition_id = payload.competition_id
    item.team_id = payload.team_id
    db.commit()
    db.refresh(item)
    return StandingOut.model_validate(item)


@router.delete("/standings/{standing_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_standing(standing_id: int, db: Session = Depends(get_db)):
    item = db.get(Standing, standing_id)
    if not item:
        raise HTTPException(status_code=404, detail="Standing not found")
    db.delete(item)
    db.commit()
    return None


@router.get("/venues", response_model=list[VenueOut])
def list_venues(db: Session = Depends(get_db)):
    return db.query(Venue).order_by(Venue.name.asc()).all()


@router.post("/venues", response_model=VenueOut, status_code=status.HTTP_201_CREATED)
def create_venue(payload: VenueCreate, db: Session = Depends(get_db)):
    item = Venue(
        name=payload.name,
        city=payload.city,
        country=payload.country,
        capacity=payload.capacity,
        address=payload.address,
        surface=payload.surface,
        image_url=payload.image_url,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/venues/{venue_id}", response_model=VenueOut)
def update_venue(venue_id: int, payload: VenueUpdate, db: Session = Depends(get_db)):
    item = db.get(Venue, venue_id)
    if not item:
        raise HTTPException(status_code=404, detail="Venue not found")
    item.name = payload.name
    item.city = payload.city
    item.country = payload.country
    item.capacity = payload.capacity
    item.address = payload.address
    item.surface = payload.surface
    item.image_url = payload.image_url
    db.commit()
    db.refresh(item)
    return item


@router.delete("/venues/{venue_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_venue(venue_id: int, db: Session = Depends(get_db)):
    item = db.get(Venue, venue_id)
    if not item:
        raise HTTPException(status_code=404, detail="Venue not found")
    db.delete(item)
    db.commit()
    return None


def _to_fixture_out(db: Session, fixture: Fixture) -> FixtureOut:
    home_team = db.get(Team, fixture.home_team_id)
    away_team = db.get(Team, fixture.away_team_id)
    venue = db.get(Venue, fixture.venue_id)
    season = db.get(Season, fixture.season_id)
    competition = db.get(Competition, fixture.competition_id)
    item = FixtureOut.model_validate(fixture)
    item.home_team_name = home_team.name if home_team else None
    item.away_team_name = away_team.name if away_team else None
    item.venue_name = venue.name if venue else None
    item.season_label = season.label if season else None
    item.competition_name = competition.name if competition else None
    return item


@router.get("/fixtures", response_model=list[FixtureOut])
def list_fixtures(db: Session = Depends(get_db)):
    fixtures = db.query(Fixture).order_by(Fixture.match_datetime.desc()).all()
    return [_to_fixture_out(db, fixture) for fixture in fixtures]


@router.post("/fixtures", response_model=FixtureOut, status_code=status.HTTP_201_CREATED)
def create_fixture(payload: FixtureCreate, db: Session = Depends(get_db)):
    item = Fixture(
        home_score=payload.home_score,
        away_score=payload.away_score,
        match_datetime=payload.match_datetime,
        status=FixtureStatus(payload.status),
        matchweek=payload.matchweek,
        round_name=payload.round_name,
        referee=payload.referee,
        attendance=payload.attendance,
        home_team_id=payload.home_team_id,
        away_team_id=payload.away_team_id,
        venue_id=payload.venue_id,
        season_id=payload.season_id,
        competition_id=payload.competition_id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return _to_fixture_out(db, item)


@router.put("/fixtures/{fixture_id}", response_model=FixtureOut)
def update_fixture(fixture_id: int, payload: FixtureUpdate, db: Session = Depends(get_db)):
    item = db.get(Fixture, fixture_id)
    if not item:
        raise HTTPException(status_code=404, detail="Fixture not found")
    item.home_score = payload.home_score
    item.away_score = payload.away_score
    item.match_datetime = payload.match_datetime
    item.status = FixtureStatus(payload.status)
    item.matchweek = payload.matchweek
    item.round_name = payload.round_name
    item.referee = payload.referee
    item.attendance = payload.attendance
    item.home_team_id = payload.home_team_id
    item.away_team_id = payload.away_team_id
    item.venue_id = payload.venue_id
    item.season_id = payload.season_id
    item.competition_id = payload.competition_id
    db.commit()
    db.refresh(item)
    return _to_fixture_out(db, item)


@router.delete("/fixtures/{fixture_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fixture(fixture_id: int, db: Session = Depends(get_db)):
    item = db.get(Fixture, fixture_id)
    if not item:
        raise HTTPException(status_code=404, detail="Fixture not found")
    db.delete(item)
    db.commit()
    return None