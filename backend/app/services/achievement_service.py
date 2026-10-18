# KAN-34: Achievement sync.

'''
 # Is for loading achievement definitions and each player's progress
   into Postgres for every played game that has achievements.
'''
# Loads achievement definitions and each player's progress into Postgres for
# every played game that has achievements.


from datetime import datetime, timezone
from typing import NamedTuple

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models import Achievement, Game, Player, PlayerAchievement, PlayerGame
from app.schemas.achievement import GameProgressOut
from app.services import player_service, steam_data
from app.services.steam_client import PrivateProfileError


class SyncResult(NamedTuple):
    synced: int
    skipped: int


def played_games_with_achievements(db: Session, steam_id: str) -> list[int]:
    """Return app IDs the player has played that have achievements."""
    stmt = (
        select(PlayerGame.app_id)
        .join(Game, Game.app_id == PlayerGame.app_id) # Join to filter for games that have achievements
        .where( # Filter for the player's games that have achievements and non-zero playtime
            PlayerGame.steam_id == int(steam_id),
            PlayerGame.playtime_minutes > 0,
            Game.has_achievements.is_(True),
        )
        .order_by(PlayerGame.app_id)
    )
    return list(db.scalars(stmt)) # Return a list of app IDs that the player has played and have achievements


def sync_game_schema(db: Session, app_id: int) -> int:
    """Load a game's achievement definitions and upsert them. Returns the row count."""
    rows = {}
    for item in steam_data.get_game_schema(app_id): # Loop through each achievement definition returned by the Steam API for the given app_id
        api_name = item["name"]
        rows[api_name] = { # Create a dictionary for each achievement definition with the relevant fields
            "app_id": app_id,
            "api_name": api_name,
            "display_name": item.get("displayName") or api_name,
            "description": item.get("description"),  # Steam can omit it
            "icon_url": item.get("icon"),
            "hidden": bool(item.get("hidden", 0)),
        }

    if rows: # If there are any achievement definitions to upsert,
        # create an insert statement for the Achievement table with the values from the rows dictionary
        stmt = insert(Achievement).values(list(rows.values()))
        db.execute(stmt.on_conflict_do_update(
            index_elements=[Achievement.app_id, Achievement.api_name],
            set_={
                "display_name": stmt.excluded.display_name,
                "description": stmt.excluded.description,
                "icon_url": stmt.excluded.icon_url,
                "hidden": stmt.excluded.hidden,
            },
        ))
    db.commit()
    return len(rows)


def sync_player_game(db: Session, steam_id: str, app_id: int) -> int:
    """Load one player's progress for a game and upsert it. Returns the row count."""
    entries = steam_data.get_player_achievements(steam_id, app_id)

    # The composite foreign key needs a matching achievements row, so skip
    # anything that isn't in the game's stored schema.
    known = set(db.scalars(
        select(Achievement.api_name).where(Achievement.app_id == app_id)
    ))

    rows = {} # Create a dictionary to hold the player's achievement progress for the given app_id
    for entry in entries:
        api_name = entry.get("apiname")
        if api_name not in known:
            continue
        unlock_time = entry.get("unlocktime") or 0
        rows[api_name] = {  # Create a dictionary for each achievement progress entry with the relevant fields
            "steam_id": int(steam_id),
            "app_id": app_id,
            "api_name": api_name,
            "achieved": bool(entry.get("achieved", 0)),
            "unlocked_at": (
                datetime.fromtimestamp(unlock_time, tz=timezone.utc)
                if unlock_time else None
            ),
        }

    if rows: # If there are any achievement progress entries to upsert,
        stmt = insert(PlayerAchievement).values(list(rows.values()))
        db.execute(stmt.on_conflict_do_update(
            index_elements=[ # Specify the composite primary key for the PlayerAchievement table to handle conflicts
                PlayerAchievement.steam_id,
                PlayerAchievement.app_id,
                PlayerAchievement.api_name,
            ],
            set_={
                "achieved": stmt.excluded.achieved,
                "unlocked_at": stmt.excluded.unlocked_at,
            },
        ))
    db.commit()
    return len(rows)


def sync_achievements(db: Session, steam_id: str) -> SyncResult:
    """Sync every played game with achievements, skipping games Steam refuses."""
    synced = skipped = 0
    for app_id in played_games_with_achievements(db, steam_id): #
        # Sync the game's achievement definitions and the player's progress for that game,
        # handling any PrivateProfileError exceptions that may occur
        try:
            sync_game_schema(db, app_id)
            sync_player_game(db, steam_id, app_id)
        except PrivateProfileError:
            db.rollback()
            skipped += 1
        else:
            synced += 1
    return SyncResult(synced, skipped)


def sync_player_data(db: Session, steam_id: str) -> Player | None:
    """Sync the profile, library and achievements. Returns None if the profile is missing."""
    # sync_library runs sync_player itself, and only after Steam confirms the
    # game details are visible, so a private profile is never saved.
    player = player_service.sync_library(db, steam_id)
    if player is None:
        return None
    sync_achievements(db, steam_id)
    return player


def get_achievement_progress(db: Session, steam_id: str) -> list[GameProgressOut]:
    """Return unlocked and total counts for each game the player has progress for."""
    total = (
        select(Achievement.app_id, func.count().label("total"))
        .group_by(Achievement.app_id)
        .subquery()
    )
    progress = ( # Create a subquery to count the number of unlocked achievements for each game the player has progress for
        select(
            PlayerAchievement.app_id,
            func.count().filter(PlayerAchievement.achieved.is_(True)).label("unlocked"),
        )
        .where(PlayerAchievement.steam_id == int(steam_id))
        .group_by(PlayerAchievement.app_id)
        .subquery()
    )
    stmt = (
        select(Game.app_id, Game.name, progress.c.unlocked, total.c.total)
        .select_from(Game)
        .join(total, total.c.app_id == Game.app_id)
        .join(progress, progress.c.app_id == Game.app_id)
        .order_by(Game.app_id)
    )
    return [GameProgressOut.model_validate(row) for row in db.execute(stmt).mappings()]
