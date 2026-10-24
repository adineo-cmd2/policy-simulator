from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PolicySubmission(Base):
    __tablename__ = "policy_submissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), index=True
    )
    policy_text: Mapped[str] = mapped_column(Text, default="")
    jurisdiction: Mapped[str] = mapped_column(String(255), default="")
    policy_domain: Mapped[str] = mapped_column(String(50), default="general")
    context: Mapped[str] = mapped_column(Text, default="")
