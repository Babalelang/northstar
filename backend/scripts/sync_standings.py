"""
Run this straight from the backend/ folder with:
    python -m scripts.sync_standings

Pulls the current South African Premiership table from TheSportsDB and
writes it into the standings table. Same logic the POST /api/standings/sync
endpoint uses - this just lets it run without the api server up, e.g. from
a cron job or a Windows Task Scheduler entry.
"""

from database.database import Session_Local
from services.standings_service import sync_standings

if __name__ == "__main__":
    db = Session_Local()
    try:
        synced = sync_standings(db)
        print(f"synced {synced} teams")
    finally:
        db.close()
