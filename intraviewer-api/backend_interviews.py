import os

MODELS_DIR = "app/models"
ROUTES_DIR = "app/api/routes"

interview_models = """
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
    evaluation_details = Column(Text, nullable=True) # JSON
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    
    application = relationship("Application")
"""

interview_routes = """
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import require_candidate
from app.models.user import User
from app.models.application import Application
from app.models.job import Job
from app.models.interview_blueprint import InterviewBlueprint
from app.models.interview_session import InterviewSession
from app.core.errors import ok, ApiError
from pydantic import BaseModel
import json
from datetime import datetime, timezone

router = APIRouter(tags=["Interviews"])

class MessageRequest(BaseModel):
    message: str

@router.post("/applications/{application_id}/start-interview")
def start_interview(application_id: str, db: Session = Depends(get_db), current_user: User = Depends(require_candidate)):
    app = db.query(Application).filter(Application.id == application_id, Application.candidate_id == current_user.id).first()
    if not app:
        raise ApiError(404, "Application not found")
        
    if app.status != "SHORTLISTED":
        raise ApiError(400, "Only shortlisted candidates can start the interview")
        
    existing = db.query(InterviewSession).filter(InterviewSession.application_id == application_id).first()
    if existing:
        return ok("Interview session retrieved", {"session_id": existing.id})
        
    session = InterviewSession(
        application_id=application_id,
        status="SCHEDULED",
        transcript=json.dumps([])
    )
    db.add(session)
    db.commit()
    
    return ok("Interview session created", {"session_id": session.id})

@router.get("/interviews/{session_id}")
def get_interview(session_id: str, db: Session = Depends(get_db)):
    # In a real app we'd secure this, but for MVP it's via a unique link
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise ApiError(404, "Interview session not found")
        
    app = db.query(Application).filter(Application.id == session.application_id).first()
    job = db.query(Job).filter(Job.id == app.job_id).first()
    candidate = db.query(User).filter(User.id == app.candidate_id).first()
    
    return ok("Session details", {
        "status": session.status,
        "job_title": job.title if job else "Role",
        "company_name": "Company", # Simplification
        "candidate_name": candidate.name if candidate else "Candidate",
        "transcript": json.loads(session.transcript) if session.transcript else []
    })

@router.post("/interviews/{session_id}/message")
def send_message(session_id: str, payload: MessageRequest, db: Session = Depends(get_db)):
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise ApiError(404, "Session not found")
        
    if session.status == "COMPLETED":
        raise ApiError(400, "Interview already completed")
        
    if session.status == "SCHEDULED":
        session.status = "IN_PROGRESS"
        session.started_at = datetime.now(timezone.utc)
        
    transcript = json.loads(session.transcript) if session.transcript else []
    
    if payload.message:
        transcript.append({"role": "user", "content": payload.message})
        
    # Very basic AI logic for MVP without Groq to ensure speed and reliability in browser
    # In production, we would pass the transcript to Groq/LLaMA
    
    turn = len([m for m in transcript if m["role"] == "user"])
    
    ai_response = ""
    is_completed = False
    
    if turn == 0:
        ai_response = "Hi there! I'm Alex, your AI recruiter. I'm excited to learn more about you. To start, could you tell me a little bit about yourself and your background?"
    elif turn == 1:
        ai_response = "That's great! Are you comfortable with a hybrid work model and the standard working hours for this role?"
    elif turn == 2:
        ai_response = "Perfect. I see from your resume that you have experience with some of our required technologies. Can you describe a challenging technical problem you recently solved?"
    elif turn == 3:
        ai_response = "Interesting approach. If you had to design a scalable backend system for thousands of concurrent users, what key components would you focus on?"
    else:
        ai_response = "Thank you so much for your time today! That concludes our interview. The team will review your responses and get back to you shortly."
        is_completed = True
        session.status = "COMPLETED"
        session.completed_at = datetime.now(timezone.utc)
        session.evaluation_score = 85 # Mock score
        
    transcript.append({"role": "assistant", "content": ai_response})
    session.transcript = json.dumps(transcript)
    db.commit()
    
    return ok("Message processed", {
        "response": ai_response,
        "is_completed": is_completed
    })
"""

with open(f"{MODELS_DIR}/interview_session.py", "w") as f:
    f.write(interview_models)

with open(f"{MODELS_DIR}/__init__.py", "a") as f:
    f.write("\nfrom app.models.interview_session import InterviewSession\n")

with open(f"{ROUTES_DIR}/interviews.py", "w") as f:
    f.write(interview_routes)

print("Backend files generated")
