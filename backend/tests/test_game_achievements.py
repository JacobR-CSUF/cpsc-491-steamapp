# KAN-42: Test game achievements endpoint.

'''
# Test for the game achievements endpoint.
  Ensures that achievements are returned in the correct order:
  unlocked newest first, then locked by name.
'''

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
from app.services import achievement_service

STEAM_ID = "76561199999999990" # Test player's Steam ID
APP_ID = 990042001             # Test game's App ID
UNOWNED_APP_ID = 990042002     # Unowned game's App ID
EARLIER = datetime(2026, 10, 1, 12) # Earlier unlock date for a test achievement
LATEST = datetime(2026, 10, 2, 12)  # Latest unlock date for a test achievement


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
                persona_name="KAN-42 Test Player",
                visibility=3,
            ))
            session.add_all([
                Game(app_id=APP_ID, name="Test Game", has_achievements=True),
                Game(app_id=UNOWNED_APP_ID, name="Unowned Game", has_achievements=True),
            ])
            session.flush()

            session.add(PlayerGame(
                steam_id=int(STEAM_ID),
                app_id=APP_ID,
                playtime_minutes=120,
                recent_playtime_minutes=0,
            ))
            session.add_all([
                Achievement(
                    app_id=app_id,
                    api_name=api_name,
                    display_name=display_name,
                    description=description,
                    icon_url=f"https://example.com/{api_name}.jpg",
                    hidden=hidden,
                )
                for app_id, api_name, display_name, description, hidden in [
                    (APP_ID, "OLD", "Old One", "Unlocked first", False),
                    (APP_ID, "NEW", "New One", "Unlocked last", False),
                    (APP_ID, "ZETA", "Zeta", None, True),
                    (APP_ID, "ALPHA", "Alpha", "Locked, has progress row", False),
                    (APP_ID, "NO_ROW", "Beta", "Locked, no progress row", False),
                    (UNOWNED_APP_ID, "OTHER", "Other", None, False),
                ]
            ])
            session.flush()

            session.add_all([
                PlayerAchievement(
                    steam_id=int(STEAM_ID), app_id=APP_ID, api_name="OLD",
                    achieved=True, unlocked_at=EARLIER,
                ),
                PlayerAchievement(
                    steam_id=int(STEAM_ID), app_id=APP_ID, api_name="NEW",
                    achieved=True, unlocked_at=LATEST,
                ),
                PlayerAchievement(
                    steam_id=int(STEAM_ID), app_id=APP_ID, api_name="ZETA",
                    achieved=False, unlocked_at=None,
                ),
                PlayerAchievement(
                    steam_id=int(STEAM_ID), app_id=APP_ID, api_name="ALPHA",
                    achieved=False, unlocked_at=None,
                ),
            ])
            session.commit()
            yield session
    finally:
        engine.dispose()


@pytest.fixture
def client(db, monkeypatch):
    # The sync is tested in test_achievements.py, so skip Steam here.
    monkeypatch.setattr(
        achievement_service,
        "sync_player_data",
        lambda db, steam_id: db.get(Player, int(steam_id)),
    )

    def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)


def test_game_achievements_order(client):
    response = client.get(f"/api/players/{STEAM_ID}/games/{APP_ID}/achievements")

    assert response.status_code == 200
    data = response.json()
    # Unlocked newest first, then locked by name.
    assert [a["api_name"] for a in data] == ["NEW", "OLD", "ALPHA", "NO_ROW", "ZETA"]
    assert data[0] == {
        "api_name": "NEW",
        "display_name": "New One",
        "description": "Unlocked last",
        "icon_url": "https://example.com/NEW.jpg",
        "hidden": False,
        "achieved": True,
        "unlocked_at": LATEST.isoformat(),
    }
    assert data[1]["unlocked_at"] == EARLIER.isoformat()
    # A locked achievement with no progress row still shows up.
    no_row = data[3]
    assert no_row["achieved"] is False
    assert no_row["unlocked_at"] is None
    # A hidden achievement with no description comes back as null.
    assert data[4]["hidden"] is True
    assert data[4]["description"] is None


def test_game_achievements_unowned_returns_404(client):
    response = client.get(
        f"/api/players/{STEAM_ID}/games/{UNOWNED_APP_ID}/achievements"
    )

    assert response.status_code == 404


def test_achievements_rejects_bad_id(client):
    assert client.get("/api/players/123/achievements").status_code == 422
    assert client.get("/api/players/123/games/1/achievements").status_code == 422
    assert client.get(f"/api/players/{STEAM_ID}/games/0/achievements").status_code == 422
