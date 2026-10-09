from __future__ import annotations

from typing import Any

import httpx

from app.core.config import get_settings

STEAM_API_BASE = "https://api.steampowered.com"


class SteamApiError(RuntimeError):
    """Raised when Steam returns an error or cannot be reached."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        detail: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.detail = detail or message


class PrivateProfileError(SteamApiError):
    """Raised when a Steam profile hides game or achievement details."""


http_client = httpx.Client(timeout=15.0)


def _error_detail(response: httpx.Response) -> str:
    """Extract a useful error message from a Steam HTTP response."""
    try:
        payload = response.json()
    except ValueError:
        return response.text.strip() or f"HTTP {response.status_code}"

    if isinstance(payload, dict):
        for key in ("error", "message", "detail"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

        playerstats = payload.get("playerstats")
        if isinstance(playerstats, dict):
            error = playerstats.get("error")
            if isinstance(error, str) and error.strip():
                return error.strip()

    return response.text.strip() or f"HTTP {response.status_code}"


def request_steam(
    interface: str,
    method: str,
    version: str,
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Send a GET request to a Steam Web API method and return its JSON body."""
    api_key = get_settings().steam_api_key
    if not api_key:
        raise SteamApiError("STEAM_API_KEY is not configured.")

    query_params: dict[str, Any] = dict(params or {})
    query_params["key"] = api_key
    url = f"{STEAM_API_BASE}/{interface}/{method}/{version}/"

    try:
        response = http_client.get(url, params=query_params)
    except httpx.RequestError as exc:
        raise SteamApiError(f"Could not reach the Steam API: {exc}") from exc

    if response.is_error:
        detail = _error_detail(response)
        raise SteamApiError(
            f"Steam API returned HTTP {response.status_code}: {detail}",
            status_code=response.status_code,
            detail=detail,
        )

    try:
        data = response.json()
    except ValueError as exc:
        raise SteamApiError("Steam API returned invalid JSON.") from exc

    if not isinstance(data, dict):
        raise SteamApiError("Steam API returned an unexpected response format.")

    return data


def get_player_summary(steam_id: str) -> dict[str, Any] | None:
    """Return one player's summary, or None when Steam returns no player."""
    data = request_steam(
        "ISteamUser",
        "GetPlayerSummaries",
        "v2",
        {"steamids": steam_id},
    )
    players = data.get("response", {}).get("players", [])
    return players[0] if players else None


def get_owned_games(steam_id: str) -> list[dict[str, Any]]:
    """Return a player's owned games, raising when game details are private."""
    data = request_steam(
        "IPlayerService",
        "GetOwnedGames",
        "v1",
        {
            "steamid": steam_id,
            "include_appinfo": 1,
            "include_played_free_games": 1,
        },
    )

    response = data.get("response", {})
    games = response.get("games") if isinstance(response, dict) else None
    if games is None:
        raise PrivateProfileError("Steam game details are private.")
    if not isinstance(games, list):
        raise SteamApiError("Steam API returned an invalid games list.")

    return games


def get_player_achievements(steam_id: str, app_id: int | str) -> list[dict[str, Any]]:
    """Return player achievements for a game, handling Steam's special errors."""
    try:
        data = request_steam(
            "ISteamUserStats",
            "GetPlayerAchievements",
            "v1",
            {
                "steamid": steam_id,
                "appid": app_id,
                "l": "english",
            },
        )
    except SteamApiError as exc:
        detail = exc.detail.lower()
        if exc.status_code == 400 and "requested app has no stats" in detail:
            return []
        if exc.status_code == 403 and "profile is not public" in detail:
            raise PrivateProfileError("Steam profile is not public.") from exc
        raise

    playerstats = data.get("playerstats", {})
    achievements = (
        playerstats.get("achievements", []) if isinstance(playerstats, dict) else []
    )
    return achievements if isinstance(achievements, list) else []


def get_game_schema(app_id: int | str) -> list[dict[str, Any]]:
    """Return the achievement schema for a Steam app."""
    data = request_steam(
        "ISteamUserStats",
        "GetSchemaForGame",
        "v2",
        {
            "appid": app_id,
            "l": "english",
        },
    )

    game = data.get("game", {})
    if not isinstance(game, dict):
        return []

    available_stats = game.get("availableGameStats", {})
    if not isinstance(available_stats, dict):
        return []

    achievements = available_stats.get("achievements", [])
    return achievements if isinstance(achievements, list) else []
