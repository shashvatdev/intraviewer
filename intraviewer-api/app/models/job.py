
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Float, Text, Enum
from sqlalchemy.orm import relationship
import enum
from app.db.base import Base
from datetime import datetime, timezone
import uuid

def utc_now():
    return datetime.now(timezone.utc)

class JobStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    PAUSED = "PAUSED"
    EXPIRED = "EXPIRED"
    CLOSED = "CLOSED"

class Job(Base):
    __tablename__ = "jobs"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    department = Column(String(255), nullable=True)
    ctc_type = Column(String(50), nullable=True)
    ctc_min = Column(String(50), nullable=True)
    ctc_max = Column(String(50), nullable=True)
    currency = Column(String(20), default="INR")
    work_start_time = Column(String(20), nullable=True)
    work_end_time = Column(String(20), nullable=True)
    timezone = Column(String(50), nullable=True)
    shift_type = Column(String(50), nullable=True)
    work_mode = Column(String(50), nullable=True)
    location = Column(String(255), nullable=True)
    relocation_required = Column(Boolean, default=False)
    deadline = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), default=JobStatus.DRAFT.value)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    
    # Relationships
    description = relationship("JobDescription", back_populates="job", uselist=False, cascade="all, delete-orphan")
    analysis = relationship("JdAnalysis", back_populates="job", uselist=False, cascade="all, delete-orphan")
    blueprint = relationship("InterviewBlueprint", back_populates="job", uselist=False, cascade="all, delete-orphan")
