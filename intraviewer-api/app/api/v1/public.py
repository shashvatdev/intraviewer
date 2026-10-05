from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.interview_session import InterviewSession
from app.models.question import Question
from app.schemas.all import SessionResponse
from app.core.security import get_current_organization
from app.models.organization import Organization
import datetime

router = APIRouter(tags=["Public Candidate Interview"])

@router.post("/sessions/{id}/invite")
def invite_session(id: str, db: Session = Depends(get_db), org: Organization = Depends(get_current_organization)):
    obj = db.query(InterviewSession).filter(InterviewSession.id == id, InterviewSession.organization_id == org.id).first()
    if not obj: raise HTTPException(status_code=404)
    return {"invite_url": f"/public/interviews/{obj.public_token}"}

@router.get("/public/interviews/{token}", response_model=SessionResponse)
def get_public_interview(token: str, db: Session = Depends(get_db)):
    obj = db.query(InterviewSession).filter(InterviewSession.public_token == token).first()
    if not obj: raise HTTPException(status_code=404)
    return obj

@router.post("/public/interviews/{token}/start")
def start_public_interview(token: str, db: Session = Depends(get_db)):
    session = db.query(InterviewSession).filter(InterviewSession.public_token == token).first()
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    if session.status != "pending": raise HTTPException(status_code=400, detail="Interview already started or completed")
    
    session.status = "in_progress"
    session.started_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(session)
    
    question = db.query(Question).filter(
        Question.interview_id == session.interview_id,
        Question.is_dynamic == False
    ).order_by(Question.id).first()
    
    return {
        "session_id": session.id,
        "question": {
            "id": question.id,
            "text": question.text,
            "type": question.question_type
        } if question else None
    }
