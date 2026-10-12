from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models import Game, Player, PlayerGame
from app.schemas import OwnedGameOut
from app.services import steam_data


def sync_player(db: Session, steam_id: str) -> Player | None:
    """Fetch a Steam profile and persist it, returning None if it is missing."""
    summary = steam_data.get_player_summary(steam_id)
    if summary is None:
        return None

    stmt = insert(Player).values(
        steam_id=int(summary["steamid"]),
        persona_name=summary["personaname"],
        avatar_url=summary.get("avatarfull"),
        profile_url=summary.get("profileurl"),
        visibility=summary["communityvisibilitystate"],
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=[Player.steam_id],
        set_={
            "persona_name": stmt.excluded.persona_name,
            "avatar_url": stmt.excluded.avatar_url,
            "profile_url": stmt.excluded.profile_url,
            "visibility": stmt.excluded.visibility,
            "updated_at": func.now(),
        },
    ).returning(Player)
    player = db.scalars(stmt, execution_options={"populate_existing": True}).one()
    db.commit()
    return player


def sync_library(db: Session, steam_id: str) -> Player | None:
    """Persist Steam's library, creating the owning player when necessary."""
    owned_games = steam_data.get_owned_games(steam_id)
    player = sync_player(db, steam_id)
    if player is None:
        return None

    games = []
    player_games = []
    for game in owned_games:
        app_id = game["appid"]
        icon_hash = game.get("img_icon_url")
        last_played = game.get("rtime_last_played")
        games.append({
            "app_id": app_id,
            "name": game["name"],
            "icon_url": (
                "https://media.steampowered.com/steamcommunity/public/images/apps/"
                f"{app_id}/{icon_hash}.jpg" if icon_hash else None
            ),
        })
        player_games.append({
            "steam_id": int(steam_id),
            "app_id": app_id,
            "playtime_minutes": game.get("playtime_forever", 0),
            "recent_playtime_minutes": game.get("playtime_2weeks", 0),
            "last_played_at": (
                datetime.fromtimestamp(last_played, tz=timezone.utc)
                if last_played else None
            ),
        })

    if games:
        stmt = insert(Game).values(games)
        db.execute(stmt.on_conflict_do_update(
            index_elements=[Game.app_id],
            set_={
                "name": stmt.excluded.name,
                "icon_url": stmt.excluded.icon_url,
                "updated_at": func.now(),
            },
        ))
        stmt = insert(PlayerGame).values(player_games)
        db.execute(stmt.on_conflict_do_update(
            index_elements=[PlayerGame.steam_id, PlayerGame.app_id],
            set_={
                "playtime_minutes": stmt.excluded.playtime_minutes,
                "recent_playtime_minutes": stmt.excluded.recent_playtime_minutes,
                "last_played_at": stmt.excluded.last_played_at,
            },
        ))
    db.commit()
    return player


def get_library(db: Session, steam_id: str) -> list[OwnedGameOut]:
    """Read the saved library in descending order of total playtime."""
    stmt = (
        select(
            Game.app_id, Game.name, Game.icon_url,
            PlayerGame.playtime_minutes, PlayerGame.recent_playtime_minutes,
            PlayerGame.last_played_at,
        )
        .join(PlayerGame, PlayerGame.app_id == Game.app_id)
        .where(PlayerGame.steam_id == int(steam_id))
        .order_by(PlayerGame.playtime_minutes.desc(), Game.app_id)
    )
    return [OwnedGameOut.model_validate(row) for row in db.execute(stmt).mappings()]
