from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.steam_id import SteamIdPath
from app.db.session import get_db
from app.schemas import OwnedGameOut, PlayerOut
from app.schemas.profile import ProfileStatusOut
from app.services import player_service
from app.services.profile_status import STATUS_MESSAGES, get_profile_status
from app.services.steam_client import PrivateProfileError, SteamApiError

router = APIRouter(prefix="/api/players", tags=["players"])


@router.get("/{steam_id}", response_model=PlayerOut)
def read_player(steam_id: SteamIdPath, db: Session = Depends(get_db)) -> PlayerOut:
    try:
        player = player_service.sync_player(db, steam_id)
    except SteamApiError as exc:
        raise HTTPException(status_code=502, detail="Steam API is unavailable.") from exc
    if player is None:
        raise HTTPException(status_code=404, detail="Steam profile not found.")
    return PlayerOut.model_validate(player)


@router.get("/{steam_id}/games", response_model=list[OwnedGameOut])
def read_library(
    steam_id: SteamIdPath,
    db: Session = Depends(get_db),
) -> list[OwnedGameOut]:
    try:
        player = player_service.sync_library(db, steam_id)
    except PrivateProfileError as exc:
        raise HTTPException(status_code=403, detail="Steam game details are private.") from exc
    except SteamApiError as exc:
        raise HTTPException(status_code=502, detail="Steam API is unavailable.") from exc
    if player is None:
        raise HTTPException(status_code=404, detail="Steam profile not found.")
    return player_service.get_library(db, steam_id)


@router.get("/{steam_id}/status", response_model=ProfileStatusOut)
def read_profile_status(steam_id: SteamIdPath) -> ProfileStatusOut:
    try:
        status = get_profile_status(steam_id)
    except SteamApiError as exc:
        raise HTTPException(status_code=502, detail="Steam API is unavailable.") from exc

    return ProfileStatusOut(
        steam_id=steam_id,
        status=status,
        message=STATUS_MESSAGES[status],
    )
