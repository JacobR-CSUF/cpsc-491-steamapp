from datetime import datetime

from pydantic import BaseModel


class PlaytimePointOut(BaseModel):
    api_name: str
    display_name: str
    unlocked_at: datetime
    estimated_hours: float


class PlaytimeGraphOut(BaseModel):
    app_id: int
    total_hours: float
    estimated: bool
    points: list[PlaytimePointOut]