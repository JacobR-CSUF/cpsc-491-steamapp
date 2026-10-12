from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select, update

from app.db.session import SessionLocal
from app.main import app
from app.models import Game, Player, PlayerGame
from app.services import steam_data
from app.services.steam_client import PrivateProfileError, SteamApiError

STEAM_ID = "76561199999999999"
APP_IDS = [-31001, -31002, -31003]
SUMMARY = {
    "steamid": STEAM_ID,
    "personaname": "KAN-31 Test Player",
    "avatarfull": "https://example.com/avatar.jpg",
    "profileurl": f"https://steamcommunity.com/profiles/{STEAM_ID}/",
    "communityvisibilitystate": 3,
}


@pytest.fixture(autouse=True)
def remove_test_player():
    with SessionLocal() as db:
        assert db.get(Player, int(STEAM_ID)) is None, "Test player already exists"
        assert not db.scalars(select(Game).where(Game.app_id.in_(APP_IDS))).all()
    try:
        yield
    finally:
        with SessionLocal() as db:
            # The player_games foreign key cascades this deletion.
            db.execute(delete(Player).where(Player.steam_id == int(STEAM_ID)))
            db.execute(delete(Game).where(Game.app_id.in_(APP_IDS)))
            db.commit()


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(steam_data, "get_player_summary", lambda steam_id: SUMMARY.copy())
    with TestClient(app) as client:
        yield client


def test_read_player_returns_profile(client):
    response = client.get(f"/api/players/{STEAM_ID}")
    assert response.status_code == 200
    assert response.json() == {
        "steam_id": STEAM_ID,
        "persona_name": SUMMARY["personaname"],
        "avatar_url": SUMMARY["avatarfull"],
        "profile_url": SUMMARY["profileurl"],
        "visibility": 3,
    }
    with SessionLocal() as db:
        player = db.get(Player, int(STEAM_ID))
        assert player.persona_name == SUMMARY["personaname"]
        assert player.avatar_url == SUMMARY["avatarfull"]
        assert player.profile_url == SUMMARY["profileurl"]
        assert player.visibility == 3


def test_read_player_updates_existing_profile(client, monkeypatch):
    assert client.get(f"/api/players/{STEAM_ID}").status_code == 200
    old_timestamp = datetime(2000, 1, 1, tzinfo=timezone.utc)
    with SessionLocal() as db:
        db.execute(update(Player).where(Player.steam_id == int(STEAM_ID)).values(
            updated_at=old_timestamp,
        ))
        db.commit()
    updated = {**SUMMARY, "personaname": "New Name", "avatarfull": None,
               "profileurl": None, "communityvisibilitystate": 1}
    monkeypatch.setattr(steam_data, "get_player_summary", lambda steam_id: updated)
    response = client.get(f"/api/players/{STEAM_ID}")
    assert response.status_code == 200
    assert response.json()["persona_name"] == "New Name"
    with SessionLocal() as db:
        player = db.get(Player, int(STEAM_ID))
        assert player.persona_name == "New Name"
        assert player.avatar_url is None
        assert player.profile_url is None
        assert player.visibility == 1
        assert player.updated_at > old_timestamp


def test_read_player_missing_returns_404(client, monkeypatch):
    monkeypatch.setattr(steam_data, "get_player_summary", lambda steam_id: None)
    assert client.get(f"/api/players/{STEAM_ID}").status_code == 404
    with SessionLocal() as db:
        assert db.get(Player, int(STEAM_ID)) is None


def test_read_library_private_returns_403(client, monkeypatch):
    def private_games(steam_id):
        raise PrivateProfileError("Steam game details are private.")

    monkeypatch.setattr(steam_data, "get_owned_games", private_games)
    assert client.get(f"/api/players/{STEAM_ID}/games").status_code == 403
    with SessionLocal() as db:
        assert db.get(Player, int(STEAM_ID)) is None


def test_read_library_saves_and_updates_games(client, monkeypatch):
    games = [
        {"appid": APP_IDS[0], "name": "First", "img_icon_url": "abc",
         "playtime_forever": 10, "rtime_last_played": 0},
        {"appid": APP_IDS[1], "name": "Second", "img_icon_url": "def",
         "playtime_forever": 100, "playtime_2weeks": 20,
         "rtime_last_played": 1700000000},
        {"appid": APP_IDS[2], "name": "Third", "playtime_forever": 0},
    ]
    monkeypatch.setattr(steam_data, "get_owned_games", lambda steam_id: games)
    response = client.get(f"/api/players/{STEAM_ID}/games")
    assert response.status_code == 200
    data = response.json()
    assert [game["app_id"] for game in data] == [APP_IDS[1], APP_IDS[0], APP_IDS[2]]
    assert data[0] == {
        "app_id": APP_IDS[1], "name": "Second",
        "icon_url": "https://media.steampowered.com/steamcommunity/public/images/apps/"
                    f"{APP_IDS[1]}/def.jpg",
        "playtime_minutes": 100, "recent_playtime_minutes": 20,
        "last_played_at": "2023-11-14T22:13:20Z",
    }
    assert data[1]["last_played_at"] is None
    assert data[1]["recent_playtime_minutes"] == 0
    assert data[2]["last_played_at"] is None
    assert data[2]["icon_url"] is None
    with SessionLocal() as db:
        assert db.get(Player, int(STEAM_ID)) is not None
        assert db.get(Game, APP_IDS[1]).name == "Second"
        owned = db.get(PlayerGame, (int(STEAM_ID), APP_IDS[1]))
        assert owned.playtime_minutes == 100
        assert owned.last_played_at == datetime.fromtimestamp(1700000000, tz=timezone.utc)
        assert db.get(PlayerGame, (int(STEAM_ID), APP_IDS[0])).last_played_at is None
        assert db.get(PlayerGame, (int(STEAM_ID), APP_IDS[2])).last_played_at is None

    games[0].update(name="Renamed", img_icon_url="new", playtime_forever=200,
                    playtime_2weeks=50, rtime_last_played=1700000000)
    response = client.get(f"/api/players/{STEAM_ID}/games")
    assert response.status_code == 200
    assert response.json()[0]["app_id"] == APP_IDS[0]
    with SessionLocal() as db:
        assert len(db.scalars(select(PlayerGame).where(
            PlayerGame.steam_id == int(STEAM_ID),
        )).all()) == 3
        assert db.get(Game, APP_IDS[0]).name == "Renamed"
        assert db.get(Game, APP_IDS[0]).icon_url.endswith("/new.jpg")
        owned = db.get(PlayerGame, (int(STEAM_ID), APP_IDS[0]))
        assert owned.playtime_minutes == 200
        assert owned.recent_playtime_minutes == 50
        assert owned.last_played_at == datetime.fromtimestamp(1700000000, tz=timezone.utc)


def test_read_library_empty_returns_empty_list(client, monkeypatch):
    monkeypatch.setattr(steam_data, "get_owned_games", lambda steam_id: [])
    response = client.get(f"/api/players/{STEAM_ID}/games")
    assert response.status_code == 200
    assert response.json() == []


def test_read_library_missing_player_returns_404(client, monkeypatch):
    monkeypatch.setattr(steam_data, "get_owned_games", lambda steam_id: [])
    monkeypatch.setattr(steam_data, "get_player_summary", lambda steam_id: None)
    assert client.get(f"/api/players/{STEAM_ID}/games").status_code == 404


@pytest.mark.parametrize("suffix", ["", "/games"])
def test_steam_failure_returns_502(client, monkeypatch, suffix):
    def unavailable(steam_id):
        raise SteamApiError("Steam unavailable")

    monkeypatch.setattr(steam_data, "get_player_summary", unavailable)
    monkeypatch.setattr(steam_data, "get_owned_games", unavailable)
    assert client.get(f"/api/players/{STEAM_ID}{suffix}").status_code == 502
