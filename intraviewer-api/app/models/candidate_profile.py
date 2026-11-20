from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import uuid4

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import UTCDateTime, utcnow

if TYPE_CHECKING:
    from app.models.user import User


class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    phone: Mapped[Optional[str]] = mapped_column(String(32))
    profile_photo: Mapped[Optional[str]] = mapped_column(String(500))
    # skills: ["Python", "React"]
    skills: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    # education: [{institution, degree, field, start_year, end_year}]
    education: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    # experience: [{company, title, start_date, end_date, current, description}]
    experience: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    github_url: Mapped[Optional[str]] = mapped_column(String(500))
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500))
    portfolio_url: Mapped[Optional[str]] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime(), default=utcnow, onupdate=utcnow, nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="candidate_profile")
