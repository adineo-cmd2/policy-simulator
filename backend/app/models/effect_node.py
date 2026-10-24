from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class EffectNode(Base):
    __tablename__ = "effect_nodes"

    id: Mapped[int] = mapped_column(primary_key=True)
    model_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("impact_models.id"), index=True
    )
    parent_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("effect_nodes.id"), nullable=True, index=True
    )
    order: Mapped[int] = mapped_column(Integer, default=1)
    title: Mapped[str] = mapped_column(String(255), default="")
    detail: Mapped[str] = mapped_column(Text, default="")
    domain_area: Mapped[str] = mapped_column(String(50), default="")
    magnitude: Mapped[str] = mapped_column(String(20), default="unknown")
    direction: Mapped[str] = mapped_column(String(20), default="mixed")
    confidence: Mapped[str] = mapped_column(String(20), default="speculative")
    analogy: Mapped[str] = mapped_column(Text, default="")
