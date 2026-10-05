from uuid import uuid4
from sqlalchemy import String, ForeignKey, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Interview(Base):
    __tablename__ = "interviews"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=True)
    job_description: Mapped[str] = mapped_column(String, nullable=True)
    skills: Mapped[str] = mapped_column(String(1000), nullable=True)
    difficulty: Mapped[str] = mapped_column(String(50), nullable=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=True)
    blueprint: Mapped[dict] = mapped_column(JSON, nullable=True)
