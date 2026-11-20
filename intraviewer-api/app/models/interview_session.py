
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime, timezone
import uuid

def utc_now():
    return datetime.now(timezone.utc)

class InterviewSession(Base):
    __tablename__ = "interview_sessions"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    application_id = Column(String(36), ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), default="SCHEDULED") # SCHEDULED, IN_PROGRESS, COMPLETED
    transcript = Column(Text, nullable=True) # JSON array of messages
    evaluation_score = Column(Integer, nullable=True)
    integrity_score = Column(Integer, default=100)
    proctoring_logs = Column(Text, nullable=True)
    evaluation_details = Column(Text, nullable=True) # JSON
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    
    application = relationship("Application")
