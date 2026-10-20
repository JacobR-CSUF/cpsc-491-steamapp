from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Achievement, Game, PlayerAchievement, PlayerGame
from app.services.achievement_service import sync_player_data
from app.services.screenshots import get_screenshots


def get_owned_game(db: Session, steam_id: str, app_id: int):
    """Return the player's library row and game, or None if unowned."""
    stmt = (
        select(PlayerGame, Game)
        .join(Game, Game.app_id == PlayerGame.app_id)
        .where(
            PlayerGame.steam_id == int(steam_id),
            PlayerGame.app_id == app_id,
        )
    )
    return db.execute(stmt).one_or_none()

def last_achievement(db: Session, steam_id: str, app_id: int):
    """Return the most recently unlocked achievement, or None."""
    stmt = (
        select(
            Achievement.api_name,
            Achievement.display_name,
            PlayerAchievement.unlocked_at,
        )
        .join(
            PlayerAchievement,
            (PlayerAchievement.app_id == Achievement.app_id)
            & (PlayerAchievement.api_name == Achievement.api_name),
        )
        .where(
            PlayerAchievement.steam_id == int(steam_id),
            PlayerAchievement.app_id == app_id,
            PlayerAchievement.achieved.is_(True),
        )
        .order_by(
            PlayerAchievement.unlocked_at.desc().nulls_last(),
            Achievement.api_name,
        )
        .limit(1)
    )
    return db.execute(stmt).mappings().one_or_none()

def game_progress(db: Session, steam_id: str, app_id: int) -> tuple[int, int]:
    """Return the player's unlocked count and the game's total count."""
    unlocked = db.scalar(
        select(func.count())
        .select_from(PlayerAchievement)
        .where(
            PlayerAchievement.steam_id == int(steam_id),
            PlayerAchievement.app_id == app_id,
            PlayerAchievement.achieved.is_(True),
        )
    )
    total = db.scalar(
        select(func.count())
        .select_from(Achievement)
        .where(Achievement.app_id == app_id)
    )
    return unlocked, total

def get_game_detail(db: Session, steam_id: str, app_id: int):
    """Sync the player and combine their details for one owned game."""
    if sync_player_data(db, steam_id) is None:
        return None

    owned_game = get_owned_game(db, steam_id, app_id)
    if owned_game is None:
        return None

    player_game, game = owned_game
    unlocked, total = game_progress(db, steam_id, app_id)
    latest = last_achievement(db, steam_id, app_id)

    return {
        "steam_id": steam_id,
        "app_id": game.app_id,
        "name": game.name,
        "icon_url": game.icon_url,
        "playtime_minutes": player_game.playtime_minutes,
        "recent_playtime_minutes": player_game.recent_playtime_minutes,
        "last_played_at": player_game.last_played_at,
        "played_recently": player_game.recent_playtime_minutes > 0,
        "achievements_unlocked": unlocked,
        "achievements_total": total,
        "last_achievement": dict(latest) if latest is not None else None,
        "screenshots": get_screenshots(steam_id, app_id),
    }