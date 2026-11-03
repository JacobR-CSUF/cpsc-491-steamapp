# KAN-34: Achievement sync.

# Does not include the player's progress, just the definitions. See achievement_service.py for that.
'''
 # Is for loading achievement definitions and each player's progress
   into Postgres for every played game that has achievements.
'''

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from app.core.steam_id import SteamIdPath
from app.db.session import get_db
from app.schemas.achievement import AchievementOut, GameProgressOut
from app.services import achievement_service
from app.services.steam_client import PrivateProfileError, SteamApiError

router = APIRouter(prefix="/api/players", tags=["achievements"])


# Default route for getting a player's achievement progress. Syncs the player's data from Steam, then returns progress per game.
@router.get("/{steam_id}/achievements", response_model=list[GameProgressOut])
def read_achievements(
    steam_id: SteamIdPath,
    db: Session = Depends(get_db),
):
    """Sync the player's data from Steam, then return progress per game."""
    try:
        player = achievement_service.sync_player_data(db, steam_id)
    except PrivateProfileError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except SteamApiError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    if player is None: # If the player is not found after syncing, raise a 404 error
        raise HTTPException(status_code=404, detail="Steam profile not found.")

    progress = achievement_service.get_achievement_progress(db, steam_id) # Get the player's achievement progress for each game they have played that has achievements
    return sorted(progress, key=lambda game: (-game.unlocked / game.total, game.name))


# KAN-42: Every achievement in one game, for the hover dates and achievement cards.
@router.get(
    "/{steam_id}/games/{app_id}/achievements",
    response_model=list[AchievementOut],
)
def read_game_achievements( # Get all achievements for a specific game, including unlock status
    steam_id: SteamIdPath,
    app_id: Annotated[int, Path(gt=0)],
    db: Session = Depends(get_db),
):
    """Sync the player's data, then return one game's achievements with unlock status."""
    try:
        player = achievement_service.sync_player_data(db, steam_id)
    except PrivateProfileError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except SteamApiError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    achievements = ( # Get the achievements for the specific game if the player exists
        achievement_service.get_game_achievements(db, steam_id, app_id)
        if player is not None
        else None
    )
    if achievements is None: # If no achievements are found, raise a 404 error
        raise HTTPException(
            status_code=404,
            detail="Player not found or game is not owned.",
        )

    return achievements
