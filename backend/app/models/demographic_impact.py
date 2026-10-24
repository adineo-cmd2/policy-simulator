from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DemographicImpact(Base):
    __tablename__ = "demographic_impacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    model_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("impact_models.id"), index=True
    )
    effect_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("effect_nodes.id"), index=True
    )
    group_name: Mapped[str] = mapped_column(String(100), default="")
    impact_type: Mapped[str] = mapped_column(String(20), default="mixed")
    magnitude: Mapped[str] = mapped_column(String(20), default="unknown")
    explanation: Mapped[str] = mapped_column(Text, default="")
