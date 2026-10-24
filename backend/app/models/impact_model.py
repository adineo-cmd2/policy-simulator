from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ImpactModel(Base):
    __tablename__ = "impact_models"

    id: Mapped[int] = mapped_column(primary_key=True)
    submission_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("policy_submissions.id"), unique=True, index=True
    )
