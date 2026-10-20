from pydantic import BaseModel


class CompletedGameOut(BaseModel):
    app_id: int
    name: str


class PlayerStatsOut(BaseModel):
    steam_id: str
    games_owned: int
    games_played: int
    achievements_unlocked: int
    achievements_available: int
    completion_rate: float
    completed_games: list[CompletedGameOut]
