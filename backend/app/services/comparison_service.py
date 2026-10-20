from sqlalchemy import func, select
from sqlalchemy.orm import Session, aliased

from app.models import Achievement, Game, PlayerAchievement, PlayerGame
from app.schemas.comparison import ComparisonOut, SharedGameOut
from app.services import achievement_service, stats_service
from app.services.profile_status import ProfileStatus, STATUS_MESSAGES


class ComparisonProfileError(ValueError):
    def __init__(self, status: ProfileStatus):
        self.status = status
        super().__init__(STATUS_MESSAGES[status])


def shared_games(db: Session, steam_id_a: str, steam_id_b: str) -> list[SharedGameOut]:
    """Compare every shared library game, including games with no progress."""
    library_a = aliased(PlayerGame)
    library_b = aliased(PlayerGame)
    totals = (
        select(Achievement.app_id, func.count().label("total"))
        .group_by(Achievement.app_id)
        .subquery()
    )
    progress = (
        select(
            PlayerAchievement.app_id,
            func.count().filter(
                PlayerAchievement.steam_id == int(steam_id_a)
            ).label("unlocked_a"),
            func.count().filter(
                PlayerAchievement.steam_id == int(steam_id_b)
            ).label("unlocked_b"),
        )
        .where(
            PlayerAchievement.steam_id.in_([int(steam_id_a), int(steam_id_b)]),
            PlayerAchievement.achieved.is_(True),
        )
        .group_by(PlayerAchievement.app_id)
        .subquery()
    )
    unlocked_a = func.coalesce(progress.c.unlocked_a, 0)
    unlocked_b = func.coalesce(progress.c.unlocked_b, 0)
    stmt = (
        select(
            Game.app_id, Game.name,
            func.coalesce(totals.c.total, 0).label("total"),
            unlocked_a.label("unlocked_a"), unlocked_b.label("unlocked_b"),
            (unlocked_a - unlocked_b).label("difference"),
        )
        .join(library_a, library_a.app_id == Game.app_id)
        .join(library_b, library_b.app_id == Game.app_id)
        .outerjoin(totals, totals.c.app_id == Game.app_id)
        .outerjoin(progress, progress.c.app_id == Game.app_id)
        .where(
            library_a.steam_id == int(steam_id_a),
            library_b.steam_id == int(steam_id_b),
        )
        .order_by(Game.app_id)
    )
    return [SharedGameOut.model_validate(row) for row in db.execute(stmt).mappings()]


def mutual_achievements(db: Session, steam_id_a: str, steam_id_b: str) -> int:
    """Count matching unlocked achievements by both app ID and API name."""
    progress_b = aliased(PlayerAchievement)
    stmt = (
        select(func.count())
        .select_from(PlayerAchievement)
        .join(progress_b, (
            (progress_b.app_id == PlayerAchievement.app_id)
            & (progress_b.api_name == PlayerAchievement.api_name)
        ))
        .where(
            PlayerAchievement.steam_id == int(steam_id_a),
            progress_b.steam_id == int(steam_id_b),
            PlayerAchievement.achieved.is_(True),
            progress_b.achieved.is_(True),
        )
    )
    return db.scalar(stmt)


def compare_players(db: Session, steam_id_a: str, steam_id_b: str) -> ComparisonOut:
    """Sync both players and return differences as player A minus player B."""
    for steam_id in (steam_id_a, steam_id_b):
        if achievement_service.sync_player_data(db, steam_id) is None:
            raise ComparisonProfileError(ProfileStatus.not_found)

    player_a = stats_service.player_stats(db, steam_id_a)
    player_b = stats_service.player_stats(db, steam_id_b)
    return ComparisonOut(
        player_a=player_a,
        player_b=player_b,
        shared_games=shared_games(db, steam_id_a, steam_id_b),
        mutual_achievements=mutual_achievements(db, steam_id_a, steam_id_b),
        achievements_difference=player_a.achievements_unlocked - player_b.achievements_unlocked,
        completion_rate_difference=round(player_a.completion_rate - player_b.completion_rate, 1),
    )
