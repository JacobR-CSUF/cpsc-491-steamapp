# KAN-46: Advanced game stats.

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from app.core.steam_id import SteamIdPath
from app.db.session import get_db
from app.schemas.advanced import AdvancedStatsOut
from app.services import advanced_stats as advanced_service
from app.services.achievement_service import sync_player_data
from app.services.steam_client import PrivateProfileError, SteamApiError

router = APIRouter(prefix="/api/players", tags=["advanced stats"])


@router.get("/{steam_id}/games/{app_id}/advanced", response_model=AdvancedStatsOut)
def read_advanced_stats(
    steam_id: SteamIdPath,
    app_id: Annotated[int, Path(gt=0)],
    db: Session = Depends(get_db),
):
    try:
        player = sync_player_data(db, steam_id)
        stats = (
            advanced_service.advanced_stats(db, steam_id, app_id)
            if player is not None
            else None
        )
    except PrivateProfileError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except SteamApiError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    if stats is None:
        raise HTTPException(
            status_code=404,
            detail="Player not found or game is not owned.",
        )

    return stats
