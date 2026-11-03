from datetime import datetime

from pydantic import BaseModel

from app.schemas.player import PlayerOut


class ComparisonRecordOut(BaseModel):
    id: int
    compared_at: datetime
    player_a: PlayerOut
    player_b: PlayerOut


class OpponentOut(BaseModel):
    player: PlayerOut
    last_compared_at: datetime
    times_compared: int
