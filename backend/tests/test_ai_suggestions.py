from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.controllers import advanced
from app.core import cache
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import Achievement, Game, Player, PlayerAchievement, PlayerGame
from app.services import ai_suggestions, steam_data

STEAM_ID = "76561199999999987"
APP_ID = 990047001
GLOBAL_PERCENTAGES = {"FIRST": 88.4, "EASY": 61.5, "HARD": 3.2}
TIPS = "Explorer: check the map for unvisited areas.\nUntouchable: learn the boss patterns first."


class FakeRedis:  # Same in-memory stand-in as tests/test_cache.py
    def __init__(self):
        self.store = {}
        self.ttls = {}

    def get(self, key):
        return self.store.get(key)

    def set(self, key, value, ex=None):
        self.store[key] = value
        self.ttls[key] = ex


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
                persona_name="KAN-47 Test Player",
                visibility=3,
            ))
            session.add(Game(app_id=APP_ID, name="Test Game", has_achievements=True))
            session.flush()

            session.add(PlayerGame(
                steam_id=int(STEAM_ID),
                app_id=APP_ID,
                playtime_minutes=300,
            ))
            session.add_all([
                Achievement(app_id=APP_ID, api_name="FIRST", display_name="First Steps",
                            description="Finish the tutorial."),
                Achievement(app_id=APP_ID, api_name="HARD", display_name="Untouchable",
                            description="Beat the game without taking damage."),
                Achievement(app_id=APP_ID, api_name="EASY", display_name="Explorer",
                            description="Visit every area."),
            ])
            session.flush()

            # FIRST is unlocked; EASY and HARD are missing.
            session.add_all([
                PlayerAchievement(steam_id=int(STEAM_ID), app_id=APP_ID,
                                  api_name="FIRST", achieved=True),
                PlayerAchievement(steam_id=int(STEAM_ID), app_id=APP_ID,
                                  api_name="EASY", achieved=False),
            ])
            session.commit()
            yield session
    finally:
        engine.dispose()


@pytest.fixture
def gemini_calls(monkeypatch):
    """Replace request_suggestions so tests never call the Gemini API."""
    prompts = []

    def fake_request(prompt):
        prompts.append(prompt)
        return TIPS

    monkeypatch.setattr(ai_suggestions, "request_suggestions", fake_request)
    monkeypatch.setattr(
        steam_data,
        "get_global_percentages",
        lambda app_id: GLOBAL_PERCENTAGES,
    )
    return prompts


@pytest.fixture
def client(db, monkeypatch):
    monkeypatch.setattr(
        advanced,
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


def use_key(monkeypatch, key):
    monkeypatch.setattr(
        ai_suggestions,
        "get_settings",
        lambda: SimpleNamespace(gemini_api_key=key),
    )


def test_prompt_lists_easiest_first(db, gemini_calls, monkeypatch):
    monkeypatch.setattr(cache, "get_redis", lambda: FakeRedis())

    result = ai_suggestions.get_suggestions(db, STEAM_ID, APP_ID)

    assert result == {"app_id": APP_ID, "suggestions": TIPS}
    prompt = gemini_calls[0]
    assert "Test Game" in prompt
    assert "1. Explorer: Visit every area. (61.5% of players have it)" in prompt
    assert "2. Untouchable: Beat the game without taking damage. (3.2% of players have it)" in prompt
    assert "First Steps" not in prompt  # already unlocked

    # Only the 10 easiest of a longer list go into the prompt.
    many = [
        {"display_name": f"A{n}", "description": None, "global_percent": 50.0 - n}
        for n in range(12)
    ]
    capped = ai_suggestions.build_prompt("Test Game", many)
    assert "10. A9:" in capped
    assert "A10" not in capped and "A11" not in capped


def test_missing_key_returns_503(client, gemini_calls, monkeypatch):
    use_key(monkeypatch, "")

    response = client.get(f"/api/players/{STEAM_ID}/games/{APP_ID}/suggestions")

    assert response.status_code == 503
    assert gemini_calls == []


def test_suggestions_are_cached(client, gemini_calls, monkeypatch):
    use_key(monkeypatch, "test-key")
    fake = FakeRedis()
    monkeypatch.setattr(cache, "get_redis", lambda: fake)
    url = f"/api/players/{STEAM_ID}/games/{APP_ID}/suggestions"

    first = client.get(url)
    second = client.get(url)

    assert first.status_code == 200
    assert second.json() == first.json() == {"app_id": APP_ID, "suggestions": TIPS}
    assert len(gemini_calls) == 1
    key = f"ai:suggestions:{STEAM_ID}:{APP_ID}"
    assert fake.ttls[key] == 24 * 60 * 60
