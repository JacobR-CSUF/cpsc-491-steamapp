from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Comparison(Base):
    __tablename__ = "comparisons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    player_a_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("players.steam_id", ondelete="CASCADE")
    )
    player_b_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("players.steam_id", ondelete="CASCADE")
    )
    compared_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
