"""
One-off backfill: copies legacy flat Player stat columns into a
season-scoped PlayerStatistic row.
"""
import argparse

from database.database import get_db
from models import Player
from models.playerstatistic import PlayerStatistic


def backfill(season_id: int, competition_id: int, dry_run: bool = False) -> None:
    db = next(get_db())
    try:
        players = db.query(Player).order_by(Player.first_name, Player.last_name).all()

        existing_player_ids = {
            row.player_id
            for row in db.query(PlayerStatistic).filter(
                PlayerStatistic.season_id == season_id,
                PlayerStatistic.competition_id == competition_id,
            )
        }

        created, skipped = 0, 0
        for player in players:
            if player.id in existing_player_ids:
                skipped += 1
                continue

            row = PlayerStatistic(
                player_id=player.id,
                season_id=season_id,
                competition_id=competition_id,
                minutes_played=player.minutes_played or 0,
                goals=player.goals or 0,
                assists=player.assists or 0,
                saves=player.saves,
                goals_conceded=player.goals_conceded,
                clean_sheets=player.clean_sheets or 0,
                tackles=player.tackles,
                interceptions=player.interceptions,
                clearances=player.clearances,
                rating=player.form_rating,
                # not tracked on the flat Player row - defaulted, fix up manually if needed
                appearances=0,
                starts=0,
                yellow_cards=0,
                red_cards=0,
                own_goals=0,
                penalties_scored=0,
                penalties_missed=0,
            )

            action = "[dry-run] would create" if dry_run else "creating"
            print(
                f"  {action} row for {player.first_name} {player.last_name}: "
                f"goals={row.goals}, assists={row.assists}, minutes={row.minutes_played}, "
                f"saves={row.saves}, clean_sheets={row.clean_sheets}, "
                f"tackles={row.tackles}, interceptions={row.interceptions}, clearances={row.clearances}"
            )

            if not dry_run:
                db.add(row)
            created += 1

        if not dry_run:
            db.commit()

        print(
            f"\nDone. {created} row(s) {'would be ' if dry_run else ''}created, "
            f"{skipped} skipped (already had a row for this season/competition)."
        )
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--season-id", type=int, required=True, help="The OLD season's id to backfill into")
    parser.add_argument("--competition-id", type=int, required=True, help="The competition id for that season")
    parser.add_argument("--dry-run", action="store_true", help="Print what would happen without writing to the DB")
    args = parser.parse_args()
    backfill(args.season_id, args.competition_id, dry_run=args.dry_run)