import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import uuid4

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import UTCDateTime, utcnow

if TYPE_CHECKING:
    from app.models.candidate_profile import CandidateProfile
    from app.models.company_profile import CompanyProfile


class UserRole(str, enum.Enum):
    CANDIDATE = "CANDIDATE"
    COMPANY = "COMPANY"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime(), default=utcnow, onupdate=utcnow, nullable=False
    )

    candidate_profile: Mapped[Optional["CandidateProfile"]] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    company_profile: Mapped[Optional["CompanyProfile"]] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
