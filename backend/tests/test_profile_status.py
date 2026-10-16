from app.services import profile_status, steam_data
from app.services.profile_status import ProfileStatus
from app.services.steam_client import PrivateProfileError

STEAM_ID = "76561199093251857"
PUBLIC_SUMMARY = {
    "steamid": STEAM_ID,
    "communityvisibilitystate": 3,
}


def test_games_private_status(monkeypatch):
    monkeypatch.setattr(
        steam_data,
        "get_player_summary",
        lambda steam_id: PUBLIC_SUMMARY.copy(),
    )

    def private_games(steam_id):
        raise PrivateProfileError("Steam game details are private.")

    monkeypatch.setattr(steam_data, "get_owned_games", private_games)

    assert profile_status.get_profile_status(STEAM_ID) == ProfileStatus.games_private


def test_playtime_hidden_status(monkeypatch):
    monkeypatch.setattr(
        steam_data,
        "get_player_summary",
        lambda steam_id: PUBLIC_SUMMARY.copy(),
    )
    monkeypatch.setattr(
        steam_data,
        "get_owned_games",
        lambda steam_id: [
            {"appid": 10, "playtime_forever": 0},
            {"appid": 20, "playtime_forever": 0},
        ],
    )

    assert profile_status.get_profile_status(STEAM_ID) == ProfileStatus.playtime_hidden
