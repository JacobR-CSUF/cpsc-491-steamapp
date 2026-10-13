from __future__ import annotations

import re
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from app.core.cache import cached
from app.services.steam_client import SteamApiError, request_steam

ONE_HOUR = 3600


def _unique_urls(values: list[str]) -> list[str]:
    """Keep valid image URLs in their original order without duplicates."""
    urls = []
    for value in values:
        parsed = urlparse(value)
        if parsed.scheme in {"https", "http"} and parsed.netloc:
            if value not in urls:
                urls.append(value)
    return urls


def fetch_from_api(steam_id: str, app_id: int) -> list[str]:
    """Fetch screenshot file URLs through the Steam Web API."""
    data = request_steam(
        "IPublishedFileService",
        "GetUserFiles",
        "v1",
        {
            "steamid": steam_id,
            "appid": app_id,
            "filetype": 4,
            "numperpage": 10,
        },
    )

    response = data.get("response")
    if not isinstance(response, dict):
        raise SteamApiError("Steam returned an invalid screenshot response.")

    details = response.get("publishedfiledetails", [])
    if not isinstance(details, list):
        raise SteamApiError("Steam returned an invalid screenshot list.")

    urls = [
        item["file_url"]
        for item in details
        if isinstance(item, dict)
        and isinstance(item.get("file_url"), str)
        and item["file_url"]
    ]
    return _unique_urls(urls)


def parse_profile_page(html: str, app_id: int) -> list[str]:
    """Extract screenshot URLs belonging to the requested game."""
    soup = BeautifulSoup(html, "html.parser")
    urls = []

    for entry in soup.select(".profile_media_item[data-appid]"):
        if entry.get("data-appid") != str(app_id):
            continue

        image = entry.select_one(".imgWallItem")
        if image is None:
            continue

        style = image.get("style", "")
        match = re.search(
            r"""background-image\s*:\s*url\(\s*['"]?([^'")\s]+)['"]?\s*\)""",
            style,
            flags=re.IGNORECASE,
        )
        if match:
            urls.append(match.group(1))

    return _unique_urls(urls)


def fetch_from_profile_page(steam_id: str, app_id: int) -> list[str]:
    """Download and parse the player's public screenshots page."""
    url = f"https://steamcommunity.com/profiles/{steam_id}/screenshots/"

    try:
        response = httpx.get(
            url,
            params={"appid": app_id},
            timeout=15.0,
            follow_redirects=True,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise SteamApiError(
            "Could not retrieve the public screenshots page."
        ) from exc

    return parse_profile_page(response.text, app_id)


def get_screenshots(steam_id: str, app_id: int) -> list[str]:
    """Try the API, fall back to the page, and cache for one hour."""
    def fetch() -> list[str]:
        try:
            urls = fetch_from_api(steam_id, app_id)
        except SteamApiError:
            urls = []

        if urls:
            return urls

        return fetch_from_profile_page(steam_id, app_id)

    return cached(
        f"steam:screenshots:{steam_id}:{app_id}",
        ONE_HOUR,
        fetch,
    )