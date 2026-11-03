from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.steam_id import STEAM_ID_PATTERN, SteamIdPath
from app.db.session import get_db
from app.schemas.history import ComparisonRecordOut, OpponentOut
from app.services import history_service

router = APIRouter(prefix="/api", tags=["history"])


@router.get("/comparisons", response_model=list[ComparisonRecordOut])
def read_comparisons(
    steam_id: Annotated[str | None, Query(pattern=STEAM_ID_PATTERN)] = None,
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
    db: Session = Depends(get_db),
) -> list[ComparisonRecordOut]:
    return history_service.recent_comparisons(db, steam_id, limit)


@router.get("/players/{steam_id}/opponents", response_model=list[OpponentOut])
def read_opponents(
    steam_id: SteamIdPath,
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
    db: Session = Depends(get_db),
) -> list[OpponentOut]:
    return history_service.recent_opponents(db, steam_id, limit)
