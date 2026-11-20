
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime, timezone
import uuid

def utc_now():
    return datetime.now(timezone.utc)

class JdAnalysis(Base):
    __tablename__ = "jd_analysis"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), unique=True)
    required_skills = Column(Text, nullable=True) # JSON
    good_to_have_skills = Column(Text, nullable=True) # JSON
    hard_requirements = Column(Text, nullable=True) # JSON
    preferred_requirements = Column(Text, nullable=True) # JSON
    minimum_experience = Column(Integer, nullable=True)
    maximum_experience = Column(Integer, nullable=True)
    education = Column(Text, nullable=True) # JSON
    role_level = Column(String(50), nullable=True)
    domain = Column(String(100), nullable=True)
    raw_ai_response = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    
    job = relationship("Job", back_populates="analysis")
