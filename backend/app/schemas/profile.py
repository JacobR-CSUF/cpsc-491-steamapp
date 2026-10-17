from pydantic import BaseModel

from app.services.profile_status import ProfileStatus


class ProfileStatusOut(BaseModel):
    steam_id: str
    status: ProfileStatus
    message: str
