from uuid import uuid4
from sqlalchemy import String, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Question(Base):
    __tablename__ = "questions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    interview_id: Mapped[str] = mapped_column(String(36), ForeignKey("interviews.id"), nullable=False)
    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id"), nullable=False)
    text: Mapped[str] = mapped_column(String(1000), nullable=False)
    time_limit_seconds: Mapped[int] = mapped_column(Integer, nullable=True)
