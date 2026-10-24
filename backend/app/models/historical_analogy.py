from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class HistoricalAnalogy(Base):
    __tablename__ = "historical_analogies"

    id: Mapped[int] = mapped_column(primary_key=True)
    model_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("impact_models.id"), index=True
    )
    effect_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("effect_nodes.id"), index=True
    )
    title: Mapped[str] = mapped_column(String(255), default="")
    jurisdiction: Mapped[str] = mapped_column(String(255), default="")
    year: Mapped[int] = mapped_column(Integer, default=0)
    outcome: Mapped[str] = mapped_column(Text, default="")
    similarity: Mapped[str] = mapped_column(String(20), default="low")
