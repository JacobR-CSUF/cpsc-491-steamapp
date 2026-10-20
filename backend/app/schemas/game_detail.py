from datetime import datetime

from pydantic import BaseModel


class LastAchievementOut(BaseModel):
    api_name: str
    display_name: str
    unlocked_at: datetime | None


class GameDetailOut(BaseModel):
    steam_id: str
    app_id: int
    name: str
    icon_url: str | None
    playtime_minutes: int
    recent_playtime_minutes: int
    last_played_at: datetime | None
    played_recently: bool
    achievements_unlocked: int
    achievements_total: int
    last_achievement: LastAchievementOut | None
    screenshots: list[str]