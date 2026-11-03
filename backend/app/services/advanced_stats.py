# KAN-46: Advanced game stats.

# A game's achievement ratio plus the achievements the player is still
# missing, ranked by how many Steam players have unlocked each one.

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.models import Achievement, PlayerAchievement
from app.services import steam_data
from app.services.game_detail_service import game_progress, get_owned_game


def missing_achievements(db: Session, steam_id: str, app_id: int) -> list[dict]:
    """Return locked achievements with their global unlock percent, highest first."""
    stmt = (
        select(
            Achievement.api_name,
            Achievement.display_name,
            Achievement.description,
            Achievement.icon_url,
        )
        # Outer join: an achievement with no progress row is still locked.
        .outerjoin(
            PlayerAchievement,
            and_(
                PlayerAchievement.app_id == Achievement.app_id,
                PlayerAchievement.api_name == Achievement.api_name,
                PlayerAchievement.steam_id == int(steam_id),
            ),
        )
        .where(
            Achievement.app_id == app_id,
            PlayerAchievement.achieved.is_not(True),
        )
    )
    locked = [dict(row) for row in db.execute(stmt).mappings()]
    if not locked:
        return []

    percentages = steam_data.get_global_percentages(app_id)
    for achievement in locked:
        achievement["global_percent"] = percentages.get(achievement["api_name"])

    # Easiest first: highest global percent, unknown percents last, then by name.
    return sorted(
        locked,
        key=lambda a: (
            a["global_percent"] is None,
            -(a["global_percent"] or 0.0),
            a["display_name"],
        ),
    )


def advanced_stats(db: Session, steam_id: str, app_id: int) -> dict | None:
    """Return the unlocked count, total, ratio and missing achievements for one game.

    Returns None when the player doesn't own the game.
    """
    owned_game = get_owned_game(db, steam_id, app_id)
    if owned_game is None:
        return None

    _, game = owned_game
    unlocked, total = game_progress(db, steam_id, app_id)
    ratio = round(unlocked / total * 100, 1) if total else 0.0

    return {
        "app_id": game.app_id,
        "name": game.name,
        "unlocked": unlocked,
        "total": total,
        "ratio": ratio,
        "missing": missing_achievements(db, steam_id, app_id),
    }
