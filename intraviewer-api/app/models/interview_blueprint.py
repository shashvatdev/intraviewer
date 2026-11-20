
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime, timezone
import uuid

def utc_now():
    return datetime.now(timezone.utc)

class InterviewBlueprint(Base):
    __tablename__ = "interview_blueprints"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), unique=True)
    persona_level = Column(String(50), nullable=True)
    estimated_duration = Column(Integer, nullable=True)
    question_distribution = Column(Text, nullable=True) # JSON
    evaluation_weights = Column(Text, nullable=True) # JSON
    similarity_threshold = Column(Integer, default=65)
    version = Column(Integer, default=1)
    status = Column(String(50), default="DRAFT")
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    
    job = relationship("Job", back_populates="blueprint")
