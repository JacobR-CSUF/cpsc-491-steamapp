from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.controllers import playtime
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import Achievement, Game, Player, PlayerAchievement, PlayerGame

STEAM_ID = "76561199999999989"
APP_ID = 990044001
UNOWNED_APP_ID = 990044002

FIRST = datetime(2026, 10, 1, 12)
MIDDLE = datetime(2026, 10, 2, 12)
LAST = datetime(2026, 10, 3, 12)


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
                persona_name="KAN-45 Test Player",
                visibility=3,
            ))
            session.add_all([
                Game(app_id=APP_ID, name="Playtime Test Game", has_achievements=True),
                Game(app_id=UNOWNED_APP_ID, name="Unowned Test Game"),
            ])
            session.flush()

            session.add(PlayerGame(
                steam_id=int(STEAM_ID),
                app_id=APP_ID,
                playtime_minutes=120,
                recent_playtime_minutes=0,
                last_played_at=LAST,
            ))

            unlocks = [
                ("FIRST", "First Achievement", FIRST),
                ("MIDDLE", "Middle Achievement", MIDDLE),
                ("LAST", "Last Achievement", LAST),
            ]
            session.add_all([
                Achievement(
                    app_id=APP_ID,
                    api_name=api_name,
                    display_name=display_name,
                )
                for api_name, display_name, _ in unlocks
            ])
            session.flush()

            session.add_all([
                PlayerAchievement(
                    steam_id=int(STEAM_ID),
                    app_id=APP_ID,
                    api_name=api_name,
                    achieved=True,
                    unlocked_at=unlocked_at,
                )
                for api_name, _, unlocked_at in unlocks
            ])
            session.commit()
            yield session
    finally:
        engine.dispose()


@pytest.fixture
def client(db, monkeypatch):
    monkeypatch.setattr(
        playtime,
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


def test_playtime_graph_returns_points(client):
    response = client.get(f"/api/players/{STEAM_ID}/games/{APP_ID}/playtime")

    assert response.status_code == 200
    assert response.json() == {
        "app_id": APP_ID,
        "total_hours": 2.0,
        "estimated": True,
        "points": [
            {
                "api_name": "FIRST",
                "display_name": "First Achievement",
                "unlocked_at": FIRST.isoformat(),
                "estimated_hours": 0.0,
            },
            {
                "api_name": "MIDDLE",
                "display_name": "Middle Achievement",
                "unlocked_at": MIDDLE.isoformat(),
                "estimated_hours": 1.0,
            },
            {
                "api_name": "LAST",
                "display_name": "Last Achievement",
                "unlocked_at": LAST.isoformat(),
                "estimated_hours": 2.0,
            },
        ],
    }


def test_playtime_graph_unowned_returns_404(client):
    response = client.get(
        f"/api/players/{STEAM_ID}/games/{UNOWNED_APP_ID}/playtime"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Player not found or game is not owned."
    }