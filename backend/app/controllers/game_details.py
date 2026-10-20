from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from app.core.steam_id import SteamIdPath
from app.db.session import get_db
from app.schemas.game_detail import GameDetailOut
from app.services import game_detail_service
from app.services.steam_client import PrivateProfileError, SteamApiError

router = APIRouter(prefix="/api/players", tags=["game details"])


@router.get("/{steam_id}/games/{app_id}", response_model=GameDetailOut)
def read_game_detail(
    steam_id: SteamIdPath,
    app_id: Annotated[int, Path(gt=0)],
    db: Session = Depends(get_db),
):
    try:
        detail = game_detail_service.get_game_detail(db, steam_id, app_id)
    except PrivateProfileError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except SteamApiError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    if detail is None:
        raise HTTPException(
            status_code=404,
            detail="Player not found or game is not owned.",
        )

    return detail