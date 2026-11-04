# KAN-47: AI achievement suggestions.

from pydantic import BaseModel


class SuggestionsOut(BaseModel):
    app_id: int
    suggestions: str
