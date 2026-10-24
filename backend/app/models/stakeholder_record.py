from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class StakeholderRecord(Base):
    __tablename__ = "stakeholder_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    model_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("impact_models.id"), index=True
    )
    group_name: Mapped[str] = mapped_column(String(100), default="")
    stance: Mapped[str] = mapped_column(String(20), default="mixed")
    rating: Mapped[int] = mapped_column(Integer, default=0)
    explanation: Mapped[str] = mapped_column(Text, default="")
