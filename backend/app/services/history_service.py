from sqlalchemy import case, func, or_, select
from sqlalchemy.orm import Session, aliased

from app.models import Comparison, Player
from app.schemas.history import ComparisonRecordOut, OpponentOut
from app.schemas.player import PlayerOut


def record_comparison(db: Session, steam_id_a: str, steam_id_b: str) -> Comparison:
    """Save a successful comparison with the database-generated timestamp."""
    comparison = Comparison(player_a_id=int(steam_id_a), player_b_id=int(steam_id_b))
    db.add(comparison)
    db.commit()
    db.refresh(comparison)
    return comparison


def recent_comparisons(
    db: Session, steam_id: str | None = None, limit: int = 20,
) -> list[ComparisonRecordOut]:
    """Return newest comparisons and both stored profiles in a single query."""
    player_a = aliased(Player)
    player_b = aliased(Player)
    stmt = (
        select(Comparison, player_a, player_b)
        .join(player_a, player_a.steam_id == Comparison.player_a_id)
        .join(player_b, player_b.steam_id == Comparison.player_b_id)
        .order_by(Comparison.compared_at.desc(), Comparison.id.desc())
        .limit(limit)
    )
    if steam_id is not None:
        stmt = stmt.where(or_(
            Comparison.player_a_id == int(steam_id),
            Comparison.player_b_id == int(steam_id),
        ))
    return [
        ComparisonRecordOut(
            id=comparison.id,
            compared_at=comparison.compared_at,
            player_a=PlayerOut.model_validate(a),
            player_b=PlayerOut.model_validate(b),
        )
        for comparison, a, b in db.execute(stmt)
    ]


def recent_opponents(db: Session, steam_id: str, limit: int = 10) -> list[OpponentOut]:
    """Group opponents across either player position, newest encounter first."""
    player_id = int(steam_id)
    opponent_id = case(
        (Comparison.player_a_id == player_id, Comparison.player_b_id),
        else_=Comparison.player_a_id,
    )
    opponents = (
        select(
            opponent_id.label("steam_id"),
            func.max(Comparison.compared_at).label("last_compared_at"),
            func.count().label("times_compared"),
        )
        .where(or_(Comparison.player_a_id == player_id, Comparison.player_b_id == player_id))
        .group_by(opponent_id)
        .subquery()
    )
    stmt = (
        select(Player, opponents.c.last_compared_at, opponents.c.times_compared)
        .join(opponents, opponents.c.steam_id == Player.steam_id)
        .order_by(opponents.c.last_compared_at.desc(), Player.steam_id)
        .limit(limit)
    )
    return [
        OpponentOut(
            player=PlayerOut.model_validate(player),
            last_compared_at=last_compared_at,
            times_compared=times_compared,
        )
        for player, last_compared_at, times_compared in db.execute(stmt)
    ]
