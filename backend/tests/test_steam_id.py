import pytest
from fastapi.testclient import TestClient

from app.core.steam_id import parse_steam_id
from app.main import app

VALID_STEAM_ID = "76561199093251857"


def test_parse_steam_id_accepts_valid_id():
    assert parse_steam_id(f"  {VALID_STEAM_ID}  ") == int(VALID_STEAM_ID)


@pytest.mark.parametrize(
    "value",
    [
        "7656119abcdefghij",
        "7656119909325185",
        "12345679093251857",
    ],
)
def test_parse_steam_id_rejects_bad_format(value):
    with pytest.raises(ValueError):
        parse_steam_id(value)


def test_invalid_id_returns_422():
    with TestClient(app) as client:
        response = client.get("/api/players/123/status")
    assert response.status_code == 422
