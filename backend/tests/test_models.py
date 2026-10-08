from app.db.base import Base
from app.models import Achievement, Game, Player, PlayerAchievement, PlayerGame


def test_core_tables_registered():
    models = [Player, Game, PlayerGame, Achievement, PlayerAchievement]
    assert {model.__tablename__ for model in models} <= set(Base.metadata.tables)
