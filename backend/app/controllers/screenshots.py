from typing import Annotated

from fastapi import APIRouter, HTTPException, Path

from app.services.screenshots import get_screenshots
from app.services.steam_client import SteamApiError

router = APIRouter(prefix="/api/players", tags=["screenshots"])


@router.get(
    "/{steam_id}/games/{app_id}/screenshots",
    response_model=list[str],
)
def read_screenshots(
    steam_id: Annotated[str, Path(pattern=r"^[0-9]{17}$")],
    app_id: Annotated[int, Path(gt=0)],
) -> list[str]:
    try:
        return get_screenshots(steam_id, app_id)
    except SteamApiError as exc:
        raise HTTPException(
            status_code=502,
            detail="Steam screenshots are unavailable.",
        ) from exc