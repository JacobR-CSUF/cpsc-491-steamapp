import pytest
from fastapi.testclient import TestClient

from app.db.session import get_db
from app.main import create_app
from app.services import achievement_service, profile_status
from app.services.steam_client import PrivateProfileError, SteamApiError

PLAYER_A = "76561199999999995"
PLAYER_B = "76561199999999996"


@pytest.fixture
def client():
    app = create_app()

    def override_db():
        yield None

    app.dependency_overrides[get_db] = override_db

    with TestClient(app) as test_client:
        yield test_client


def test_steam_failure_returns_502(client, monkeypatch):
    def fail(steam_id):
        raise SteamApiError("Internal Steam failure")

    monkeypatch.setattr(profile_status, "get_profile_status", fail)

    response = client.get(
        "/api/compare",
        params={"player_a": PLAYER_A, "player_b": PLAYER_B},
    )

    assert response.status_code == 502
    assert response.json() == {
        "detail": "Steam couldn’t be reached. Try again in a minute."
    }


def test_private_profile_failure_returns_403(client, monkeypatch):
    def fail(steam_id):
        raise PrivateProfileError("Internal private-profile failure")

    monkeypatch.setattr(profile_status, "get_profile_status", fail)

    response = client.get(
        "/api/compare",
        params={"player_a": PLAYER_A, "player_b": PLAYER_B},
    )

    assert response.status_code == 403
    assert response.json() == {
        "detail": "This player’s game details are private."
    }


def test_achievements_rejects_wrong_prefix(client, monkeypatch):
    def unexpected(*args):
        pytest.fail("Invalid SteamID64 must be rejected before syncing")

    monkeypatch.setattr(
        achievement_service, "sync_player_data", unexpected
    )

    response = client.get(
        "/api/players/12345678901234567/achievements"
    )

    assert response.status_code == 422