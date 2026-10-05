from uuid import uuid4
import secrets
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class InterviewSession(Base):
    __tablename__ = "interview_sessions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    interview_id: Mapped[str] = mapped_column(String(36), ForeignKey("interviews.id"), nullable=False)
    candidate_id: Mapped[str] = mapped_column(String(36), ForeignKey("candidates.id"), nullable=False)
    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    public_token: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, default=lambda: secrets.token_urlsafe(32))
