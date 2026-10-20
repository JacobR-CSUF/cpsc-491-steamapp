import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.db.session import SessionLocal
from app.main import app
from app.models import Achievement, Game, Player, PlayerAchievement, PlayerGame
from app.schemas.achievement import GameProgressOut
from app.schemas.stats import CompletedGameOut
from app.services import achievement_service, stats_service
from app.services.steam_client import PrivateProfileError

STEAM_ID = "76561199999999997"
APP_IDS = [-35001, -35002, -35003]
PERFECT, PARTIAL, UNPLAYED = APP_IDS

GAMES = {PERFECT: ("Perfect", 120), PARTIAL: ("Partial", 30), UNPLAYED: ("Unplayed", 0)}
DEFINITIONS = {
    PERFECT: ["P_ONE", "P_TWO"],
    PARTIAL: ["Q_ONE", "Q_TWO", "Q_THREE"],
    UNPLAYED: ["U_ONE"],
}
PROGRESS = {
    PERFECT: {"P_ONE": True, "P_TWO": True},
    PARTIAL: {"Q_ONE": True, "Q_TWO": False, "Q_THREE": False},
}


@pytest.fixture(autouse=True)
def remove_test_rows():
    with SessionLocal() as db:
        assert db.get(Player, int(STEAM_ID)) is None, "Test player already exists"
        assert not db.scalars(select(Game).where(Game.app_id.in_(APP_IDS))).all()
    try:
        yield
    finally:
        with SessionLocal() as db:
            db.execute(delete(Player).where(Player.steam_id == int(STEAM_ID)))
            db.execute(delete(Game).where(Game.app_id.in_(APP_IDS)))
            db.commit()


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


def seed_player():
    steam_id = int(STEAM_ID)
    with SessionLocal() as db:
        db.add(Player(steam_id=steam_id, persona_name="KAN-35 Test Player", visibility=3))
        for app_id, (name, _) in GAMES.items():
            db.add(Game(app_id=app_id, name=name, has_achievements=True))
        db.flush()
        for app_id, (_, minutes) in GAMES.items():
            db.add(PlayerGame(steam_id=steam_id, app_id=app_id, playtime_minutes=minutes))
            for api_name in DEFINITIONS[app_id]:
                db.add(Achievement(app_id=app_id, api_name=api_name, display_name=api_name))
        db.flush()
        for app_id, achievements in PROGRESS.items():
            for api_name, achieved in achievements.items():
                db.add(PlayerAchievement(
                    steam_id=steam_id, app_id=app_id, api_name=api_name, achieved=achieved
                ))
        db.commit()


def test_completion_rate_handles_zero():
    assert stats_service.completion_rate(0, 0) == 0.0
    assert stats_service.completion_rate(1, 3) == 33.3
    assert stats_service.completion_rate(5, 5) == 100.0


def test_completed_games_requires_all_unlocked():
    progress = [
        GameProgressOut(app_id=1, name="Done", unlocked=4, total=4),
        GameProgressOut(app_id=2, name="Close", unlocked=3, total=4),
        GameProgressOut(app_id=3, name="Empty", unlocked=0, total=0),
    ]
    assert stats_service.completed_games(progress) == [CompletedGameOut(app_id=1, name="Done")]


def test_player_stats_totals():
    seed_player()
    with SessionLocal() as db:
        stats = stats_service.player_stats(db, STEAM_ID)

    assert stats.steam_id == STEAM_ID
    assert (stats.games_owned, stats.games_played) == (3, 2)
    assert (stats.achievements_unlocked, stats.achievements_available) == (3, 5)
    assert stats.completion_rate == 60.0
    assert stats.completed_games == [CompletedGameOut(app_id=PERFECT, name="Perfect")]


def test_read_stats_returns_stats(client, monkeypatch):
    seed_player()
    monkeypatch.setattr(
        achievement_service, "sync_player_data",
        lambda db, steam_id: db.get(Player, int(steam_id)),
    )
    response = client.get(f"/api/players/{STEAM_ID}/stats")
    assert response.status_code == 200
    assert response.json() == {
        "steam_id": STEAM_ID,
        "games_owned": 3,
        "games_played": 2,
        "achievements_unlocked": 3,
        "achievements_available": 5,
        "completion_rate": 60.0,
        "completed_games": [{"app_id": PERFECT, "name": "Perfect"}],
    }


def test_read_stats_missing_player_returns_404(client, monkeypatch):
    monkeypatch.setattr(achievement_service, "sync_player_data", lambda db, steam_id: None)
    assert client.get(f"/api/players/{STEAM_ID}/stats").status_code == 404


def test_read_stats_private_returns_403(client, monkeypatch):
    def private(db, steam_id):
        raise PrivateProfileError("Steam game details are private.")

    monkeypatch.setattr(achievement_service, "sync_player_data", private)
    assert client.get(f"/api/players/{STEAM_ID}/stats").status_code == 403


def test_read_stats_rejects_bad_id(client):
    assert client.get("/api/players/123/stats").status_code == 422
