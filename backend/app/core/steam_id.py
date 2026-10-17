import re
from typing import Annotated

from fastapi import Path

STEAM_ID_PATTERN = r"^7656119\d{10}$"
SteamIdPath = Annotated[str, Path(pattern=STEAM_ID_PATTERN)]


def parse_steam_id(value: str) -> int:
    steam_id = value.strip()
    if re.fullmatch(STEAM_ID_PATTERN, steam_id) is None:
        raise ValueError("Invalid SteamID64 format.")
    return int(steam_id)
