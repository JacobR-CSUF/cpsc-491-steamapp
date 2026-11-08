# KAN-34: Achievement sync.

'''
# Loads achievement definitions and each player's progress
  into Postgres for every played game that has achievements.
'''

from datetime import date as date_type
from datetime import datetime

from pydantic import BaseModel


class GameProgressOut(BaseModel):
    app_id: int                 # The unique identifier for the game.
    name: str                   # The name of the game.
    unlocked: int               # The number of achievements the player has unlocked in this game.
    total: int                  # The total number of achievements available in this game.

# KAN-42: One achievement in a game, with the player's unlock status.
class AchievementOut(BaseModel):
    api_name: str               # The unique identifier for the achievement in the game's API.
    display_name: str           # The name of the achievement as displayed to the player.
    description: str | None     # The description of the achievement.
    icon_url: str | None        # The URL of the achievement's icon.
    hidden: bool                # Whether the achievement is hidden from the player.
    achieved: bool              # Whether the player has achieved the achievement.
    unlocked_at: datetime | None  # The timestamp when the achievement was unlocked by the player.



# KAN-43: Daily unlock counts for the advanced graphs.
# Represents a point in time for the achievement timeline,
# including the date and the number of achievements unlocked on that date.
class TimelinePointOut(BaseModel):
    date: date_type
    unlocked: int

# Represents the timeline of achievements for a specific game,
# including the total number of achievements and the points in time when achievements were unlocked.
class AchievementTimelineOut(BaseModel):
    days: int
    app_id: int | None
    total: int
    points: list[TimelinePointOut]
