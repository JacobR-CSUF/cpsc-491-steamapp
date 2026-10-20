import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import Achievement, Game, Player, PlayerAchievement, PlayerGame
from app.services import achievement_service, comparison_service, profile_status
from app.services.profile_status import ProfileStatus, STATUS_MESSAGES
from app.services.steam_client import PrivateProfileError, SteamApiError

PLAYER_A = "76561199999999995"
PLAYER_B = "76561199999999996"
SHARED, EMPTY, A_ONLY, B_ONLY, UNSYNCED = range(-36005, -36000)


@pytest.fixture
def db():
    # Isolate comparison tests from saved Steam data and external services.
    engine = create_engine("sqlite://", poolclass=StaticPool,
                           connect_args={"check_same_thread": False})

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, _):
        connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add_all([
            Player(steam_id=int(PLAYER_A), persona_name="Player A", visibility=3),
            Player(steam_id=int(PLAYER_B), persona_name="Player B", visibility=3),
        ])
        session.add_all([
            Game(app_id=SHARED, name="Shared", has_achievements=True),
            Game(app_id=EMPTY, name="No achievements"),
            Game(app_id=A_ONLY, name="A only", has_achievements=True),
            Game(app_id=B_ONLY, name="B only", has_achievements=True),
            Game(app_id=UNSYNCED, name="No progress yet", has_achievements=True),
        ])
        session.flush()
        for steam_id, games in [
            (PLAYER_A, [SHARED, EMPTY, A_ONLY, UNSYNCED]),
            (PLAYER_B, [SHARED, EMPTY, B_ONLY, UNSYNCED]),
        ]:
            session.add_all([
                PlayerGame(steam_id=int(steam_id), app_id=app_id, playtime_minutes=60)
                for app_id in games
            ])
        for app_id, names in [
            (SHARED, ["ONE", "TWO", "THREE"]),
            (A_ONLY, ["SAME_NAME"]), (B_ONLY, ["SAME_NAME"]),
            (UNSYNCED, ["ONE"]),
        ]:
            session.add_all([
                Achievement(app_id=app_id, api_name=name, display_name=name)
                for name in names
            ])
        session.flush()
        for steam_id, app_id, values in [
            (PLAYER_A, SHARED, {"ONE": True, "TWO": True, "THREE": False}),
            (PLAYER_B, SHARED, {"ONE": True, "TWO": False, "THREE": False}),
            (PLAYER_A, A_ONLY, {"SAME_NAME": True}),
            (PLAYER_B, B_ONLY, {"SAME_NAME": True}),
        ]:
            session.add_all([
                PlayerAchievement(steam_id=int(steam_id), app_id=app_id,
                                  api_name=name, achieved=achieved)
                for name, achieved in values.items()
            ])
        session.commit()
        yield session
    engine.dispose()


@pytest.fixture
def client(db, monkeypatch):
    monkeypatch.setattr(profile_status, "get_profile_status", lambda _: ProfileStatus.public)
    monkeypatch.setattr(achievement_service, "sync_player_data",
                        lambda db, steam_id: db.get(Player, int(steam_id)))

    def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)


def test_shared_games_difference(db):
    games = [game.model_dump() for game in comparison_service.shared_games(db, PLAYER_A, PLAYER_B)]
    assert games == [
        {"app_id": SHARED, "name": "Shared", "total": 3,
         "unlocked_a": 2, "unlocked_b": 1, "difference": 1},
        {"app_id": EMPTY, "name": "No achievements", "total": 0,
         "unlocked_a": 0, "unlocked_b": 0, "difference": 0},
        {"app_id": UNSYNCED, "name": "No progress yet", "total": 1,
         "unlocked_a": 0, "unlocked_b": 0, "difference": 0},
    ]


def test_mutual_achievements_count(db):
    assert comparison_service.mutual_achievements(db, PLAYER_A, PLAYER_B) == 1


def test_same_player_returns_400(client, monkeypatch):
    def unexpected(*args):
        pytest.fail("Same-player input must be rejected before Steam calls")

    monkeypatch.setattr(profile_status, "get_profile_status", unexpected)
    monkeypatch.setattr(achievement_service, "sync_player_data", unexpected)
    assert client.get("/api/compare", params={"player_a": PLAYER_A, "player_b": PLAYER_A}).status_code == 400


def test_read_comparison(client, monkeypatch):
    synced = []

    def sync(db, steam_id):
        synced.append(steam_id)
        return db.get(Player, int(steam_id))

    monkeypatch.setattr(achievement_service, "sync_player_data", sync)
    response = client.get("/api/compare", params={"player_a": PLAYER_A, "player_b": PLAYER_B})
    assert response.status_code == 200
    assert synced == [PLAYER_A, PLAYER_B]
    data = response.json()
    assert data["player_a"] == {
        "steam_id": PLAYER_A, "games_owned": 4, "games_played": 4,
        "achievements_unlocked": 3, "achievements_available": 4,
        "completion_rate": 75.0,
        "completed_games": [{"app_id": A_ONLY, "name": "A only"}],
    }
    assert data["player_b"] == {
        "steam_id": PLAYER_B, "games_owned": 4, "games_played": 4,
        "achievements_unlocked": 2, "achievements_available": 4,
        "completion_rate": 50.0,
        "completed_games": [{"app_id": B_ONLY, "name": "B only"}],
    }
    assert len(data["shared_games"]) == 3
    assert data["mutual_achievements"] == 1
    assert data["achievements_difference"] == 1
    assert data["completion_rate_difference"] == 25.0

    reverse = client.get("/api/compare", params={"player_a": PLAYER_B, "player_b": PLAYER_A}).json()
    assert reverse["achievements_difference"] == -1
    assert reverse["completion_rate_difference"] == -25.0
    assert reverse["shared_games"][0]["difference"] == -1
    assert reverse["mutual_achievements"] == 1


@pytest.mark.parametrize("player", ["player_a", "player_b"])
@pytest.mark.parametrize("bad_id", ["123", "abc", "765611900000000000", "7656119000000000x"])
def test_invalid_id_returns_422(client, player, bad_id):
    params = {"player_a": PLAYER_A, "player_b": PLAYER_B, player: bad_id}
    assert client.get("/api/compare", params=params).status_code == 422


@pytest.mark.parametrize("missing", ["player_a", "player_b"])
def test_missing_id_returns_422(client, missing):
    params = {"player_a": PLAYER_A, "player_b": PLAYER_B}
    params.pop(missing)
    assert client.get("/api/compare", params=params).status_code == 422


@pytest.mark.parametrize("steam_id", [PLAYER_A, PLAYER_B])
@pytest.mark.parametrize("status", [
    ProfileStatus.not_found, ProfileStatus.profile_private,
    ProfileStatus.games_private, ProfileStatus.playtime_hidden,
])
def test_unreadable_profile_returns_status_message(client, monkeypatch, steam_id, status):
    monkeypatch.setattr(profile_status, "get_profile_status",
                        lambda value: status if value == steam_id else ProfileStatus.public)
    response = client.get("/api/compare", params={"player_a": PLAYER_A, "player_b": PLAYER_B})
    assert response.status_code == (404 if status == ProfileStatus.not_found else 403)
    assert response.json()["detail"] == STATUS_MESSAGES[status]


def test_profile_disappears_during_sync(client, monkeypatch):
    monkeypatch.setattr(achievement_service, "sync_player_data", lambda *args: None)
    response = client.get("/api/compare", params={"player_a": PLAYER_A, "player_b": PLAYER_B})
    assert response.status_code == 404
    assert response.json()["detail"] == STATUS_MESSAGES[ProfileStatus.not_found]


@pytest.mark.parametrize("source", ["status", "sync"])
@pytest.mark.parametrize("error, code, message", [
    (PrivateProfileError, 403, STATUS_MESSAGES[ProfileStatus.games_private]),
    (SteamApiError, 502, "Steam API is unavailable."),
])
def test_steam_error(client, monkeypatch, source, error, code, message):
    def fail(*args):
        raise error("Steam failure")

    if source == "status":
        monkeypatch.setattr(profile_status, "get_profile_status", fail)
    else:
        monkeypatch.setattr(achievement_service, "sync_player_data", fail)
    response = client.get("/api/compare", params={"player_a": PLAYER_A, "player_b": PLAYER_B})
    assert response.status_code == code
    assert response.json()["detail"] == message


def test_no_shared_games_or_mutual_achievements(db):
    db.execute(delete(PlayerGame).where(PlayerGame.steam_id == int(PLAYER_B)))
    db.execute(delete(PlayerAchievement).where(PlayerAchievement.steam_id == int(PLAYER_B)))
    db.commit()
    assert comparison_service.shared_games(db, PLAYER_A, PLAYER_B) == []
    assert comparison_service.mutual_achievements(db, PLAYER_A, PLAYER_B) == 0
