from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import PlayerGame
from app.schemas.achievement import GameProgressOut
from app.schemas.stats import CompletedGameOut, PlayerStatsOut
from app.services.achievement_service import get_achievement_progress


def achievement_totals(progress: list[GameProgressOut]) -> tuple[int, int]:
    unlocked = sum(game.unlocked for game in progress)
    available = sum(game.total for game in progress)
    return unlocked, available


def completion_rate(unlocked: int, available: int) -> float:
    if available <= 0:
        return 0.0
    return round(unlocked / available * 100, 1)


def completed_games(progress: list[GameProgressOut]) -> list[CompletedGameOut]:
    done = [game for game in progress if game.total > 0 and game.unlocked == game.total]
    return [
        CompletedGameOut(app_id=game.app_id, name=game.name)
        for game in sorted(done, key=lambda game: game.name)
    ]


def library_counts(db: Session, steam_id: str) -> tuple[int, int]:
    stmt = select(
        func.count(),
        func.count().filter(PlayerGame.playtime_minutes > 0),
    ).where(PlayerGame.steam_id == int(steam_id))
    owned, played = db.execute(stmt).one()
    return owned, played


def player_stats(db: Session, steam_id: str) -> PlayerStatsOut:
    progress = get_achievement_progress(db, steam_id)
    unlocked, available = achievement_totals(progress)
    owned, played = library_counts(db, steam_id)
    return PlayerStatsOut(
        steam_id=steam_id,
        games_owned=owned,
        games_played=played,
        achievements_unlocked=unlocked,
        achievements_available=available,
        completion_rate=completion_rate(unlocked, available),
        completed_games=completed_games(progress),
    )
