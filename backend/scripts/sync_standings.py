"""Run straight from the backend/ folder with:
    python -m scripts.sync_standings <season_id> <competition_id>

Rebuilds the standings table for one season/competition from the
full-time fixtures already stored in our own database. There's no
external service to reach anymore - this is the same recompute the
POST /api/standings/recompute endpoint runs, it just lets it run
without the api server up (e.g. from a cron job or a scheduled task).
"""

import sys

from database.database import Session_Local
from services.sync_service import sync_standings_from_fixtures

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: python -m scripts.sync_standings <season_id> <competition_id>")
        sys.exit(1)

    season_id = int(sys.argv[1])
    competition_id = int(sys.argv[2])

    db = Session_Local()
    try:
        synced = sync_standings_from_fixtures(db, season_id=season_id, competition_id=competition_id)
        print(f"recomputed standings for {synced} teams")
    finally:
        db.close()
