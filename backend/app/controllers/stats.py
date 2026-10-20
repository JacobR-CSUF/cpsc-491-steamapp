from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.steam_id import SteamIdPath
from app.db.session import get_db
from app.schemas.stats import PlayerStatsOut
from app.services import achievement_service, stats_service
from app.services.steam_client import PrivateProfileError, SteamApiError

router = APIRouter(prefix="/api/players", tags=["stats"])


@router.get("/{steam_id}/stats", response_model=PlayerStatsOut)
def read_stats(steam_id: SteamIdPath, db: Session = Depends(get_db)) -> PlayerStatsOut:
    try:
        player = achievement_service.sync_player_data(db, steam_id)
    except PrivateProfileError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except SteamApiError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    if player is None:
        raise HTTPException(status_code=404, detail="Steam profile not found.")

    return stats_service.player_stats(db, steam_id)
