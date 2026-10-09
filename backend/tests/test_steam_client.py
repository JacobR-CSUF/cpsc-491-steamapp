from types import SimpleNamespace

import httpx
import pytest

from app.services import steam_client


def _use_mock_transport(monkeypatch: pytest.MonkeyPatch, handler) -> None:
    client = httpx.Client(transport=httpx.MockTransport(handler), timeout=15.0)
    monkeypatch.setattr(steam_client, "http_client", client)
    monkeypatch.setattr(
        steam_client,
        "get_settings",
        lambda: SimpleNamespace(steam_api_key="test-api-key"),
    )


def test_get_player_summary_returns_player(monkeypatch: pytest.MonkeyPatch) -> None:
    expected_player = {
        "steamid": "76561198129224466",
        "personaname": "Test Player",
        "communityvisibilitystate": 3,
    }

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/ISteamUser/GetPlayerSummaries/v2/"
        assert request.url.params["key"] == "test-api-key"
        assert request.url.params["steamids"] == "76561198129224466"
        return httpx.Response(
            200,
            json={"response": {"players": [expected_player]}},
        )

    _use_mock_transport(monkeypatch, handler)

    player = steam_client.get_player_summary("76561198129224466")

    assert player == expected_player


def test_get_owned_games_raises_when_private(monkeypatch: pytest.MonkeyPatch) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/IPlayerService/GetOwnedGames/v1/"
        assert request.url.params["include_appinfo"] == "1"
        assert request.url.params["include_played_free_games"] == "1"
        return httpx.Response(200, json={"response": {}})

    _use_mock_transport(monkeypatch, handler)

    with pytest.raises(steam_client.PrivateProfileError):
        steam_client.get_owned_games("76561198129224466")


def test_get_player_achievements_without_stats_returns_empty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/ISteamUserStats/GetPlayerAchievements/v1/"
        assert request.url.params["l"] == "english"
        return httpx.Response(400, text="Requested app has no stats")

    _use_mock_transport(monkeypatch, handler)

    achievements = steam_client.get_player_achievements(
        "76561198129224466",
        10,
    )

    assert achievements == []
