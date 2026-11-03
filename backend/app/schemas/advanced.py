# KAN-46: Advanced game stats.

from pydantic import BaseModel


class MissingAchievementOut(BaseModel):
    api_name: str
    display_name: str
    description: str | None
    icon_url: str | None
    global_percent: float | None


class AdvancedStatsOut(BaseModel):
    app_id: int
    name: str
    unlocked: int
    total: int
    ratio: float
    missing: list[MissingAchievementOut]
