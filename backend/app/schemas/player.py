from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class PlayerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    steam_id: str
    persona_name: str
    avatar_url: str | None
    profile_url: str | None
    visibility: int

    @field_validator("steam_id", mode="before")
    @classmethod
    def stringify_steam_id(cls, value: int | str) -> str:
        return str(value)


class OwnedGameOut(BaseModel):
    app_id: int
    name: str
    icon_url: str | None
    playtime_minutes: int
    recent_playtime_minutes: int
    last_played_at: datetime | None
