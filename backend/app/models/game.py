from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String, false, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Game(Base):
    __tablename__ = "games"

    app_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(String)
    icon_url: Mapped[str | None] = mapped_column(String)
    has_achievements: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class PlayerGame(Base):
    __tablename__ = "player_games"

    steam_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("players.steam_id", ondelete="CASCADE"), primary_key=True
    )
    app_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("games.app_id", ondelete="CASCADE"), primary_key=True
    )
    playtime_minutes: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"))
    recent_playtime_minutes: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"))
    last_played_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
