from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.interview_session import InterviewSession
from app.schemas.all import SessionResponse
from app.core.security import get_current_organization
from app.models.organization import Organization

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

@router.post("/public/interviews/{token}/start", response_model=SessionResponse)
def start_public_interview(token: str, db: Session = Depends(get_db)):
    obj = db.query(InterviewSession).filter(InterviewSession.public_token == token).first()
    if not obj: raise HTTPException(status_code=404)
    obj.status = "in_progress"
    db.commit()
    db.refresh(obj)
    return obj
