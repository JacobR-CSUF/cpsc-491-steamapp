from typing import Annotated

from fastapi import APIRouter, HTTPException, Path

from app.services.screenshots import get_screenshots
from app.services.steam_client import SteamApiError
from app.core.steam_id import SteamIdPath

router = APIRouter(prefix="/api/players", tags=["screenshots"])


@router.get(
    "/{steam_id}/games/{app_id}/screenshots",
    response_model=list[str],
)
def read_screenshots(
    steam_id: SteamIdPath,
    app_id: Annotated[int, Path(gt=0)],
) -> list[str]:
    try:
        return get_screenshots(steam_id, app_id)
    except SteamApiError as exc:
        raise HTTPException(
            status_code=502,
            detail="Steam screenshots are unavailable.",
        ) from exc