
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime, timezone
import uuid

def utc_now():
    return datetime.now(timezone.utc)

class Application(Base):
    __tablename__ = "applications"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    candidate_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    resume_filename = Column(String(255), nullable=True)
    resume_text = Column(Text, nullable=True)
    match_score = Column(Integer, default=0)
    match_analysis = Column(Text, nullable=True) # JSON reasoning
    status = Column(String(50), default="APPLIED") # APPLIED, SHORTLISTED, REJECTED, INTERVIEW_SCHEDULED
    created_at = Column(DateTime(timezone=True), default=utc_now)
    
    job = relationship("Job")
    candidate = relationship("User")
