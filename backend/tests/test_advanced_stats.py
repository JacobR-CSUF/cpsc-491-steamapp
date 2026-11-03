import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.controllers import advanced
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import Achievement, Game, Player, PlayerAchievement, PlayerGame
from app.services import steam_data

STEAM_ID = "76561199999999988"
APP_ID = 990046001
UNOWNED_APP_ID = 990046002
GLOBAL_PERCENTAGES = {"FIRST": 88.4, "EASY": 61.5, "HARD": 3.2}


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
                persona_name="KAN-46 Test Player",
                visibility=3,
            ))
            session.add_all([
                Game(app_id=APP_ID, name="Test Game", has_achievements=True),
                Game(app_id=UNOWNED_APP_ID, name="Unowned Game"),
            ])
            session.flush()

            session.add(PlayerGame(
                steam_id=int(STEAM_ID),
                app_id=APP_ID,
                playtime_minutes=300,
            ))
            session.add_all([
                Achievement(
                    app_id=APP_ID,
                    api_name="FIRST",
                    display_name="First Steps",
                    description="Finish the tutorial.",
                ),
                Achievement(
                    app_id=APP_ID,
                    api_name="HARD",
                    display_name="Untouchable",
                    description="Beat the game without taking damage.",
                    icon_url="https://example.com/hard.jpg",
                ),
                Achievement(
                    app_id=APP_ID,
                    api_name="EASY",
                    display_name="Explorer",
                    description="Visit every area.",
                    icon_url="https://example.com/easy.jpg",
                ),
            ])
            session.flush()

            # FIRST is unlocked, EASY has a locked progress row, and HARD has
            # no progress row at all; both of the last two count as missing.
            session.add_all([
                PlayerAchievement(
                    steam_id=int(STEAM_ID),
                    app_id=APP_ID,
                    api_name="FIRST",
                    achieved=True,
                ),
                PlayerAchievement(
                    steam_id=int(STEAM_ID),
                    app_id=APP_ID,
                    api_name="EASY",
                    achieved=False,
                ),
            ])
            session.commit()
            yield session
    finally:
        engine.dispose()


@pytest.fixture
def client(db, monkeypatch):
    monkeypatch.setattr(
        advanced,
        "sync_player_data",
        lambda db, steam_id: db.get(Player, int(steam_id)),
    )
    monkeypatch.setattr(
        steam_data,
        "get_global_percentages",
        lambda app_id: GLOBAL_PERCENTAGES,
    )

    def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)


def test_missing_sorted_easiest_first(client):
    response = client.get(f"/api/players/{STEAM_ID}/games/{APP_ID}/advanced")

    assert response.status_code == 200
    assert response.json()["missing"] == [
        {
            "api_name": "EASY",
            "display_name": "Explorer",
            "description": "Visit every area.",
            "icon_url": "https://example.com/easy.jpg",
            "global_percent": 61.5,
        },
        {
            "api_name": "HARD",
            "display_name": "Untouchable",
            "description": "Beat the game without taking damage.",
            "icon_url": "https://example.com/hard.jpg",
            "global_percent": 3.2,
        },
    ]


def test_ratio_rounds_to_one_decimal(client):
    response = client.get(f"/api/players/{STEAM_ID}/games/{APP_ID}/advanced")

    assert response.status_code == 200
    data = response.json()
    assert data["app_id"] == APP_ID
    assert data["name"] == "Test Game"
    assert data["unlocked"] == 1
    assert data["total"] == 3
    assert data["ratio"] == 33.3


def test_advanced_unowned_returns_404(client):
    response = client.get(
        f"/api/players/{STEAM_ID}/games/{UNOWNED_APP_ID}/advanced"
    )

    assert response.status_code == 404
