
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime, timezone
import uuid

def utc_now():
    return datetime.now(timezone.utc)

class JobDescription(Base):
    __tablename__ = "job_descriptions"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), unique=True)
    source_type = Column(String(50), nullable=False) # PDF, DOCX, TXT, RICH_TEXT
    original_filename = Column(String(255), nullable=True)
    raw_text = Column(Text, nullable=False)
    structured_text = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    
    job = relationship("Job", back_populates="description")
