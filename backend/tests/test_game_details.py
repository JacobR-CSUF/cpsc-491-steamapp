from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import Achievement, Game, Player, PlayerAchievement, PlayerGame
from app.services import game_detail_service

STEAM_ID = "76561199999999994"
APP_ID = 730
UNOWNED_APP_ID = 731
EARLIER = datetime(2026, 10, 1, 12)
LATEST = datetime(2026, 10, 2, 12)
SCREENSHOTS = ["https://example.com/screenshot.jpg"]


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, _):
        connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)

    try:
        with Session(engine) as session:
            session.add(Player(
                steam_id=int(STEAM_ID),
                persona_name="KAN-37 Test Player",
                visibility=3,
            ))
            session.add_all([
                Game(
                    app_id=APP_ID,
                    name="Test Game",
                    icon_url="https://example.com/icon.jpg",
                    has_achievements=True,
                ),
                Game(app_id=UNOWNED_APP_ID, name="Unowned Game"),
            ])
            session.flush()

            session.add(PlayerGame(
                steam_id=int(STEAM_ID),
                app_id=APP_ID,
                playtime_minutes=120,
                recent_playtime_minutes=0,
                last_played_at=LATEST,
            ))
            session.add_all([
                Achievement(
                    app_id=APP_ID,
                    api_name=api_name,
                    display_name=display_name,
                )
                for api_name, display_name in [
                    ("FIRST", "First Achievement"),
                    ("LATEST", "Latest Achievement"),
                    ("LOCKED", "Locked Achievement"),
                ]
            ])
            session.flush()

            session.add_all([
                PlayerAchievement(
                    steam_id=int(STEAM_ID),
                    app_id=APP_ID,
                    api_name="FIRST",
                    achieved=True,
                    unlocked_at=EARLIER,
                ),
                PlayerAchievement(
                    steam_id=int(STEAM_ID),
                    app_id=APP_ID,
                    api_name="LATEST",
                    achieved=True,
                    unlocked_at=LATEST,
                ),
                PlayerAchievement(
                    steam_id=int(STEAM_ID),
                    app_id=APP_ID,
                    api_name="LOCKED",
                    achieved=False,
                    unlocked_at=None,
                ),
            ])
            session.commit()
            yield session
    finally:
        engine.dispose()


@pytest.fixture
def client(db, monkeypatch):
    monkeypatch.setattr(
        game_detail_service,
        "sync_player_data",
        lambda db, steam_id: db.get(Player, int(steam_id)),
    )
    monkeypatch.setattr(
        game_detail_service,
        "get_screenshots",
        lambda steam_id, app_id: SCREENSHOTS,
    )

    def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)


def test_detail_returns_last_achievement(client):
    response = client.get(f"/api/players/{STEAM_ID}/games/{APP_ID}")

    assert response.status_code == 200
    assert response.json() == {
        "steam_id": STEAM_ID,
        "app_id": APP_ID,
        "name": "Test Game",
        "icon_url": "https://example.com/icon.jpg",
        "playtime_minutes": 120,
        "recent_playtime_minutes": 0,
        "last_played_at": LATEST.isoformat(),
        "played_recently": False,
        "achievements_unlocked": 2,
        "achievements_total": 3,
        "last_achievement": {
            "api_name": "LATEST",
            "display_name": "Latest Achievement",
            "unlocked_at": LATEST.isoformat(),
        },
        "screenshots": SCREENSHOTS,
    }


def test_detail_unowned_game_returns_404(client):
    response = client.get(
        f"/api/players/{STEAM_ID}/games/{UNOWNED_APP_ID}"
    )

    assert response.status_code == 404


def test_played_recently_without_last_played(client, db):
    player_game = db.get(PlayerGame, (int(STEAM_ID), APP_ID))
    player_game.recent_playtime_minutes = 45
    player_game.last_played_at = None
    db.commit()

    response = client.get(f"/api/players/{STEAM_ID}/games/{APP_ID}")

    assert response.status_code == 200
    data = response.json()
    assert data["recent_playtime_minutes"] == 45
    assert data["last_played_at"] is None
    assert data["played_recently"] is True