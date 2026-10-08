from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    String,
    false,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Achievement(Base):
    __tablename__ = "achievements"

    app_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("games.app_id", ondelete="CASCADE"), primary_key=True
    )
    api_name: Mapped[str] = mapped_column(String, primary_key=True)
    display_name: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(String)
    icon_url: Mapped[str | None] = mapped_column(String)
    hidden: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false())


class PlayerAchievement(Base):
    __tablename__ = "player_achievements"
    __table_args__ = (
        ForeignKeyConstraint(
            ["app_id", "api_name"],
            ["achievements.app_id", "achievements.api_name"],
            ondelete="CASCADE",
        ),
    )

    steam_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("players.steam_id", ondelete="CASCADE"), primary_key=True
    )
    app_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    api_name: Mapped[str] = mapped_column(String, primary_key=True)
    achieved: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false())
    unlocked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
