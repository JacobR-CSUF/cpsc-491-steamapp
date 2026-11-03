from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import PlayerAchievement, PlayerGame


def estimate_end(
    last_played_at: datetime | None,
    recent_playtime_minutes: int,
    last_unlock: datetime,
    now: datetime,
) -> datetime:
    """Choose the endpoint for spreading total playtime."""
    if last_played_at is not None:
        return last_played_at
    if recent_playtime_minutes > 0:
        return now
    return last_unlock


def estimate_hours(
    unlocked_at: datetime,
    total_minutes: int,
    start: datetime,
    end: datetime,
) -> float:
    """Estimate cumulative hours at an unlock, rounded to one decimal."""
    total_hours = total_minutes / 60

    if start == end:
        return round(total_hours, 1)

    fraction = (
        (unlocked_at - start).total_seconds()
        / (end - start).total_seconds()
    )
    fraction = max(0.0, min(1.0, fraction))

    return round(total_hours * fraction, 1)


def playtime_curve(db: Session, steam_id: str, app_id: int):
    """Return unlocked achievements with estimated cumulative hours."""
    player_game = db.get(PlayerGame, (int(steam_id), app_id))
    if player_game is None:
        return None

    stmt = (
        select(PlayerAchievement)
        .where(
            PlayerAchievement.steam_id == int(steam_id),
            PlayerAchievement.app_id == app_id,
            PlayerAchievement.achieved.is_(True),
            PlayerAchievement.unlocked_at.is_not(None),
        )
        .order_by(PlayerAchievement.unlocked_at)
    )
    unlocks = db.scalars(stmt).all()

    if not unlocks:
        return []

    start = unlocks[0].unlocked_at
    end = estimate_end(
        player_game.last_played_at,
        player_game.recent_playtime_minutes,
        unlocks[-1].unlocked_at,
        datetime.now(timezone.utc),
    )

    if len(unlocks) == 1:
        end = start

    return [
        {
            "api_name": achievement.api_name,
            "unlocked_at": achievement.unlocked_at,
            "estimated_hours": estimate_hours(
                achievement.unlocked_at,
                player_game.playtime_minutes,
                start,
                end,
            ),
        }
        for achievement in unlocks
    ]