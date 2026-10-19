# KAN-34: Achievement sync.

'''
# Loads achievement definitions and each player's progress
  into Postgres for every played game that has achievements.
'''

from pydantic import BaseModel


class GameProgressOut(BaseModel):
    app_id: int
    name: str
    unlocked: int
    total: int
