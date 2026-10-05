from uuid import uuid4
from sqlalchemy import String, ForeignKey, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Answer(Base):
    __tablename__ = "answers"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("interview_sessions.id"), nullable=False)
    question_id: Mapped[str] = mapped_column(String(36), ForeignKey("questions.id"), nullable=False)
    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id"), nullable=False)
    video_url: Mapped[str] = mapped_column(String(1000), nullable=True)
    audio_url: Mapped[str] = mapped_column(String(1000), nullable=True)
    text_answer: Mapped[str] = mapped_column(String(2000), nullable=True)
    ai_score: Mapped[float] = mapped_column(Float, nullable=True)
    ai_strengths: Mapped[list] = mapped_column(JSON, nullable=True)
    ai_weaknesses: Mapped[list] = mapped_column(JSON, nullable=True)
    ai_feedback: Mapped[str] = mapped_column(String, nullable=True)
