from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

from sqlalchemy.orm import Session

from app.models import PlayerAchievement, PlayerGame
from app.services.playtime_estimate import (
    estimate_end,
    estimate_hours,
    playtime_curve,
)


def test_hours_spread_evenly():
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    end = start + timedelta(days=10)

    assert estimate_hours(start, 600, start, end) == 0.0
    assert estimate_hours(
        start + timedelta(days=5), 600, start, end
    ) == 5.0
    assert estimate_hours(end, 600, start, end) == 10.0

    # Round to one decimal.
    assert estimate_hours(
        start + timedelta(days=1), 100, start, end
    ) == 0.2

    # Keep estimates within the total.
    assert estimate_hours(
        start - timedelta(days=1), 600, start, end
    ) == 0.0
    assert estimate_hours(
        end + timedelta(days=1), 600, start, end
    ) == 10.0

    # Equal start and end uses the total.
    assert estimate_hours(start, 600, start, start) == 10.0


def test_end_prefers_last_played():
    last_unlock = datetime(2026, 1, 1, tzinfo=timezone.utc)
    last_played = last_unlock + timedelta(days=5)
    now = last_unlock + timedelta(days=10)

    assert estimate_end(
        last_played, 60, last_unlock, now
    ) == last_played


def test_end_falls_back_to_last_unlock():
    last_unlock = datetime(2026, 1, 1, tzinfo=timezone.utc)
    now = last_unlock + timedelta(days=10)

    assert estimate_end(None, 0, last_unlock, now) == last_unlock
    assert estimate_end(None, 60, last_unlock, now) == now


def test_single_unlock_uses_total():
    unlocked_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    db = Mock(spec=Session)

    db.get.return_value = PlayerGame(
        steam_id=76561199999999944,
        app_id=440,
        playtime_minutes=600,
        recent_playtime_minutes=0,
        last_played_at=unlocked_at + timedelta(days=10),
    )
    db.scalars.return_value.all.return_value = [
        PlayerAchievement(
            steam_id=76561199999999944,
            app_id=440,
            api_name="FIRST",
            achieved=True,
            unlocked_at=unlocked_at,
        )
    ]

    assert playtime_curve(db, "76561199999999944", 440) == [
        {
            "api_name": "FIRST",
            "unlocked_at": unlocked_at,
            "estimated_hours": 10.0,
        }
    ]