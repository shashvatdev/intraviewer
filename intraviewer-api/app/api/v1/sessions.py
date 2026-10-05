from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_organization
from app.models.organization import Organization
from app.models.interview_session import InterviewSession
from app.schemas.all import SessionCreate, SessionResponse

router = APIRouter(tags=["Sessions"])

@router.post("/interviews/{id}/sessions", response_model=SessionResponse)
def create_session(id: str, data: SessionCreate, db: Session = Depends(get_db), org: Organization = Depends(get_current_organization)):
    obj = InterviewSession(interview_id=id, candidate_id=data.candidate_id, organization_id=org.id)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/sessions/{id}", response_model=SessionResponse)
def get_session(id: str, db: Session = Depends(get_db), org: Organization = Depends(get_current_organization)):
    obj = db.query(InterviewSession).filter(InterviewSession.id == id, InterviewSession.organization_id == org.id).first()
    if not obj: raise HTTPException(status_code=404)
    return obj

@router.post("/sessions/{id}/start", response_model=SessionResponse)
def start_session(id: str, db: Session = Depends(get_db), org: Organization = Depends(get_current_organization)):
    obj = db.query(InterviewSession).filter(InterviewSession.id == id, InterviewSession.organization_id == org.id).first()
    if not obj: raise HTTPException(status_code=404)
    obj.status = "in_progress"
    db.commit()
    db.refresh(obj)
    return obj

@router.post("/sessions/{id}/complete", response_model=SessionResponse)
def complete_session(id: str, db: Session = Depends(get_db), org: Organization = Depends(get_current_organization)):
    obj = db.query(InterviewSession).filter(InterviewSession.id == id, InterviewSession.organization_id == org.id).first()
    if not obj: raise HTTPException(status_code=404)
    obj.status = "completed"
    db.commit()
    db.refresh(obj)
    return obj
