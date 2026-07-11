"""Internal "sync" - reconciling data that lives in our own tables.

There used to be a service here that pulled tables from TheSportsDB.
That's gone: every number on the site now comes from data admins enter
through the CRUD endpoints (teams, players, fixtures, ...). The one
thing that still needs reconciling is the standings table, since it's
a derived view over fixture results rather than something typed in
directly - so this module wraps that recompute step for the API and
admin layers to call after fixture results change.
"""

from sqlalchemy.orm import Session

from services.standings_service import recompute_standings


def sync_standings_from_fixtures(db: Session, season_id: int, competition_id: int) -> int:
    """Rebuilds the standings table for a season/competition from the
    fixtures already stored in our own database. Returns how many teams
    ended up with a row.
    """
    return recompute_standings(db, season_id=season_id, competition_id=competition_id)
