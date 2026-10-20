from pydantic import BaseModel

from app.schemas.stats import PlayerStatsOut


class SharedGameOut(BaseModel):
    app_id: int
    name: str
    total: int
    unlocked_a: int
    unlocked_b: int
    difference: int


class ComparisonOut(BaseModel):
    player_a: PlayerStatsOut
    player_b: PlayerStatsOut
    shared_games: list[SharedGameOut]
    mutual_achievements: int
    achievements_difference: int
    completion_rate_difference: float
