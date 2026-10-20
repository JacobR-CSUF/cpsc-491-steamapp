from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.steam_id import STEAM_ID_PATTERN
from app.db.session import get_db
from app.schemas.comparison import ComparisonOut
from app.services import comparison_service, profile_status
from app.services.profile_status import ProfileStatus, STATUS_MESSAGES
from app.services.steam_client import PrivateProfileError, SteamApiError

router = APIRouter(prefix="/api", tags=["comparisons"])


@router.get("/compare", response_model=ComparisonOut)
def read_comparison(
    player_a: Annotated[str, Query(pattern=STEAM_ID_PATTERN)],
    player_b: Annotated[str, Query(pattern=STEAM_ID_PATTERN)],
    db: Session = Depends(get_db),
) -> ComparisonOut:
    if player_a == player_b:
        raise HTTPException(status_code=400, detail="Choose two different Steam profiles.")

    try:
        for steam_id in (player_a, player_b):
            status = profile_status.get_profile_status(steam_id)
            if status != ProfileStatus.public:
                raise HTTPException(
                    status_code=404 if status == ProfileStatus.not_found else 403,
                    detail=STATUS_MESSAGES[status],
                )
        return comparison_service.compare_players(db, player_a, player_b)
    except comparison_service.ComparisonProfileError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PrivateProfileError as exc:
        raise HTTPException(
            status_code=403, detail=STATUS_MESSAGES[ProfileStatus.games_private]
        ) from exc
    except SteamApiError as exc:
        raise HTTPException(status_code=502, detail="Steam API is unavailable.") from exc
