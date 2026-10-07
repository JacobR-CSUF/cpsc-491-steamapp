from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

STEAM_API_BASE = "https://api.steampowered.com"
REPO_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = REPO_ROOT / ".env"


def read_env_file(path: Path = ENV_FILE) -> dict[str, str]:
    """Load KEY=VALUE pairs from the root .env file if it exists."""
    values: dict[str, str] = {}

    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()

        if not key:
            continue

        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]

        values[key] = value
        os.environ.setdefault(key, value)

    return values


def call_steam(
    interface: str,
    method: str,
    version: str,
    params: dict[str, str | int],
) -> dict[str, Any]:
    """Send a GET request to a Steam Web API method and return decoded JSON."""
    query = urlencode(params)
    url = f"{STEAM_API_BASE}/{interface}/{method}/{version}/?{query}"
    request = Request(url, headers={"User-Agent": "Steam-User-Showdown/1.0"})

    try:
        with urlopen(request, timeout=15) as response:
            payload = response.read().decode("utf-8")
    except HTTPError as exc:
        if exc.code in {401, 403}:
            raise RuntimeError(
                "Steam rejected the request. Check that STEAM_API_KEY is valid."
            ) from exc
        raise RuntimeError(f"Steam API returned HTTP {exc.code}.") from exc
    except URLError as exc:
        raise RuntimeError(f"Could not reach the Steam API: {exc.reason}") from exc

    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Steam API returned invalid JSON.") from exc

    if not isinstance(data, dict):
        raise RuntimeError("Steam API returned an unexpected response format.")

    return data


def get_player_summary(api_key: str, steam_id64: str) -> dict[str, Any] | None:
    """Return the player summary for one SteamID64, or None if not found."""
    data = call_steam(
        "ISteamUser",
        "GetPlayerSummaries",
        "v2",
        {"key": api_key, "steamids": steam_id64},
    )
    players = data.get("response", {}).get("players", [])
    return players[0] if players else None


def get_owned_games(api_key: str, steam_id64: str) -> dict[str, Any]:
    """Return GetOwnedGames response data for one SteamID64."""
    data = call_steam(
        "IPlayerService",
        "GetOwnedGames",
        "v1",
        {
            "key": api_key,
            "steamid": steam_id64,
            "include_appinfo": 1,
            "include_played_free_games": 1,
        },
    )
    response = data.get("response", {})
    return response if isinstance(response, dict) else {}


def visibility_label(value: Any) -> str:
    """Convert Steam's community visibility value to a readable label."""
    return "public" if value == 3 else "private/limited"


def main() -> int:
    if len(sys.argv) != 2:
        print(f"Usage: {Path(sys.argv[0]).name} <steamid64>", file=sys.stderr)
        return 2

    steam_id64 = sys.argv[1].strip()
    if not (steam_id64.isdigit() and len(steam_id64) == 17):
        print("Error: SteamID64 must be a 17-digit number.", file=sys.stderr)
        return 2

    try:
        env_values = read_env_file()
        api_key = os.environ.get("STEAM_API_KEY") or env_values.get("STEAM_API_KEY", "")
        if not api_key:
            raise RuntimeError(
                "STEAM_API_KEY is empty. Add your Steam Web API key to the root .env file."
            )

        player = get_player_summary(api_key, steam_id64)
        if player is None:
            raise RuntimeError("No Steam profile was found for that SteamID64.")

        games = get_owned_games(api_key, steam_id64)

        print(f"Display name: {player.get('personaname', 'unknown')}")
        print(
            "Profile visibility: "
            f"{visibility_label(player.get('communityvisibilitystate'))}"
        )

        if "game_count" in games:
            print(f"Owned games: {games['game_count']}")
        else:
            print("Owned games: hidden (library is private)")

        return 0
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
