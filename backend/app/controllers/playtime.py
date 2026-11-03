from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.steam_id import SteamIdPath
from app.db.session import get_db
from app.models import Achievement, PlayerGame
from app.schemas.playtime import PlaytimeGraphOut
from app.services.achievement_service import sync_player_data
from app.services.playtime_estimate import playtime_curve
from app.services.steam_client import PrivateProfileError, SteamApiError

router = APIRouter(prefix="/api/players", tags=["playtime"])


@router.get(
    "/{steam_id}/games/{app_id}/playtime",
    response_model=PlaytimeGraphOut,
)
def read_playtime_graph(
    steam_id: SteamIdPath,
    app_id: Annotated[int, Path(gt=0)],
    db: Session = Depends(get_db),
):
    try:
        player = sync_player_data(db, steam_id)
    except PrivateProfileError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except SteamApiError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    player_game = (
        db.get(PlayerGame, (int(steam_id), app_id))
        if player is not None
        else None
    )
    if player_game is None:
        raise HTTPException(
            status_code=404,
            detail="Player not found or game is not owned.",
        )

    estimates = playtime_curve(db, steam_id, app_id)

    display_names = dict(
        db.execute(
            select(Achievement.api_name, Achievement.display_name)
            .where(Achievement.app_id == app_id)
        ).all()
    )

    return {
        "app_id": app_id,
        "total_hours": player_game.playtime_minutes / 60,
        "estimated": True,
        "points": [
            {
                "api_name": point["api_name"],
                "display_name": display_names[point["api_name"]],
                "unlocked_at": point["unlocked_at"],
                "estimated_hours": point["estimated_hours"],
            }
            for point in estimates
        ],
    }