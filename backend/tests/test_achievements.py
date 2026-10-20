# KAN-34: Achievement sync tests.

'''
Test cases for achievement synchronization.
'''

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.db.session import SessionLocal
from app.main import app
from app.models import Achievement, Game, Player, PlayerAchievement
from app.services import achievement_service, steam_data
from app.services.steam_client import PrivateProfileError, SteamApiError

STEAM_ID = "76561199999999998" # A test Steam ID that is NOT a real user.
APP_IDS = [-34001, -34002, -34003, -34004, -34005]
ALPHA, BETA, GAMMA, DELTA, ECHO = APP_IDS

SUMMARY = {
    "steamid": STEAM_ID, # A test Steam ID that is NOT a real user.
    "personaname": "KAN-34 Test Player",
    "avatarfull": "https://example.com/avatar.jpg",
    "profileurl": f"https://steamcommunity.com/profiles/{STEAM_ID}/",
    "communityvisibilitystate": 3,
}

# Alpha, Beta and Echo have achievements and playtime. Beta is refused by Steam.
# Gamma has achievements but was never played. Delta was played but has none.
OWNED_GAMES = [
    {"appid": ALPHA, "name": "Alpha", "playtime_forever": 60,
     "has_community_visible_stats": True},
    {"appid": BETA, "name": "Beta", "playtime_forever": 30,
     "has_community_visible_stats": True},
    {"appid": GAMMA, "name": "Gamma", "playtime_forever": 0,
     "has_community_visible_stats": True},
    {"appid": DELTA, "name": "Delta", "playtime_forever": 10},
    {"appid": ECHO, "name": "Echo", "playtime_forever": 5,
     "has_community_visible_stats": True},
]

SCHEMAS = {
    ALPHA: [
        {"name": "ACH_ONE", "displayName": "One", "description": "First",
         "icon": "https://example.com/1.jpg", "hidden": 0},
        {"name": "ACH_TWO", "displayName": "Two",
         "icon": "https://example.com/2.jpg", "hidden": 1},
        {"name": "ACH_THREE", "displayName": "Three", "description": "Third",
         "icon": "https://example.com/3.jpg", "hidden": 0},
    ],
    BETA: [
        {"name": "B_ONE", "displayName": "B One", "hidden": 0},
        {"name": "B_TWO", "displayName": "B Two", "hidden": 0},
    ],
    ECHO: [
        {"name": "E_ONE", "displayName": "E One", "hidden": 0},
        {"name": "E_TWO", "displayName": "E Two", "hidden": 0},
    ],
}

PLAYER_ACHIEVEMENTS = {
    ALPHA: [
        {"apiname": "ACH_ONE", "achieved": 1, "unlocktime": 1700000000},
        {"apiname": "ACH_TWO", "achieved": 0, "unlocktime": 0},
        {"apiname": "ACH_THREE", "achieved": 1, "unlocktime": 1700003600},
        # Not in Alpha's schema, so it must be ignored.
        {"apiname": "ACH_UNKNOWN", "achieved": 1, "unlocktime": 1700007200},
    ],
    ECHO: [
        {"apiname": "E_ONE", "achieved": 1, "unlocktime": 1700010000},
        {"apiname": "E_TWO", "achieved": 1, "unlocktime": 1700020000},
    ],
}

# The following function is used to simulate the behavior of the Steam API when fetching a player's achievements.
# It raises a PrivateProfileError for the BETA game to simulate a private profile scenario, while returning predefined achievement data for other games.
def fake_player_achievements(steam_id, app_id):
    if app_id == BETA:
        raise PrivateProfileError("Steam profile is not public.")
    return PLAYER_ACHIEVEMENTS[app_id]


@pytest.fixture(autouse=True)
def remove_test_player():
    with SessionLocal() as db:
        assert db.get(Player, int(STEAM_ID)) is None, "Test player already exists"
        assert not db.scalars(select(Game).where(Game.app_id.in_(APP_IDS))).all()
    try:
        yield
    finally:
        with SessionLocal() as db:
            # Foreign keys cascade to player_games, achievements and player_achievements.
            db.execute(delete(Player).where(Player.steam_id == int(STEAM_ID)))
            db.execute(delete(Game).where(Game.app_id.in_(APP_IDS)))
            db.commit()


@pytest.fixture(autouse=True)
def fake_steam(monkeypatch):
    monkeypatch.setattr(steam_data, "get_player_summary", lambda steam_id: SUMMARY.copy())
    monkeypatch.setattr(steam_data, "get_owned_games", lambda steam_id: OWNED_GAMES)
    # A KeyError here means the sync asked for a game it should have skipped.
    monkeypatch.setattr(steam_data, "get_game_schema", lambda app_id: SCHEMAS[app_id])
    monkeypatch.setattr(steam_data, "get_player_achievements", fake_player_achievements)


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client

# Test cases for achievement synchronization.
def test_sync_stores_unlock_times():
    with SessionLocal() as db:
        achievement_service.sync_player_data(db, STEAM_ID)

    with SessionLocal() as db:
        key = (int(STEAM_ID), ALPHA)
        one = db.get(PlayerAchievement, (*key, "ACH_ONE"))
        assert one.achieved is True
        assert one.unlocked_at == datetime.fromtimestamp(1700000000, tz=timezone.utc)

        two = db.get(PlayerAchievement, (*key, "ACH_TWO"))
        assert two.achieved is False
        assert two.unlocked_at is None

        assert db.get(PlayerAchievement, (*key, "ACH_UNKNOWN")) is None

        hidden = db.get(Achievement, (ALPHA, "ACH_TWO"))
        assert hidden.hidden is True
        assert hidden.description is None
        assert db.get(Achievement, (ALPHA, "ACH_ONE")).description == "First"


def test_sync_skips_refused_game():
    with SessionLocal() as db:
        achievement_service.sync_player_data(db, STEAM_ID)
        result = achievement_service.sync_achievements(db, STEAM_ID)

    assert result == (2, 1)  # Alpha and Echo synced, Beta skipped
    with SessionLocal() as db:
        refused = db.scalars(select(PlayerAchievement).where(
            PlayerAchievement.steam_id == int(STEAM_ID),
            PlayerAchievement.app_id == BETA,
        )).all()
        assert refused == []

# Test that the achievement progress counts the number of unlocked achievements correctly for each game.
def test_progress_counts_unlocked():
    with SessionLocal() as db:
        achievement_service.sync_player_data(db, STEAM_ID)
        progress = achievement_service.get_achievement_progress(db, STEAM_ID)

    by_app = {game.app_id: game for game in progress}
    assert set(by_app) == {ALPHA, ECHO}
    assert (by_app[ALPHA].unlocked, by_app[ALPHA].total) == (2, 3)
    assert (by_app[ECHO].unlocked, by_app[ECHO].total) == (2, 2)

# Test that the API endpoint for reading achievements returns the most complete games first,
# sorted by the ratio of unlocked to total achievements, and then by name.
def test_read_achievements_returns_most_complete_first(client):
    response = client.get(f"/api/players/{STEAM_ID}/achievements")
    assert response.status_code == 200
    assert response.json() == [
        {"app_id": ECHO, "name": "Echo", "unlocked": 2, "total": 2},
        {"app_id": ALPHA, "name": "Alpha", "unlocked": 2, "total": 3},
    ]

# Test that the API endpoint for reading achievements returns a 403 error when the player's profile is private,
# and that no player data is stored in the database.
def test_read_achievements_private_returns_403(client, monkeypatch):
    def private_games(steam_id):
        raise PrivateProfileError("Steam game details are private.")

    monkeypatch.setattr(steam_data, "get_owned_games", private_games)
    assert client.get(f"/api/players/{STEAM_ID}/achievements").status_code == 403
    with SessionLocal() as db:
        assert db.get(Player, int(STEAM_ID)) is None

# Test that the API endpoint for reading achievements returns a 404 error when the player's profile is missing,
# and that no player data is stored in the database.
def test_read_achievements_missing_player_returns_404(client, monkeypatch):
    monkeypatch.setattr(steam_data, "get_player_summary", lambda steam_id: None)
    assert client.get(f"/api/players/{STEAM_ID}/achievements").status_code == 404


def test_sync_skips_game_steam_fails_on(monkeypatch):
    def failing_achievements(steam_id, app_id):
        if app_id == ALPHA:
            raise SteamApiError("Steam API returned HTTP 500: Internal server error", status_code=500)
        return fake_player_achievements(steam_id, app_id)

    monkeypatch.setattr(steam_data, "get_player_achievements", failing_achievements)
    with SessionLocal() as db:
        achievement_service.sync_player_data(db, STEAM_ID)
        result = achievement_service.sync_achievements(db, STEAM_ID)

    assert result == (1, 2)
