from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_organization
from app.models.organization import Organization
from app.models.interview import Interview
from app.schemas.all import InterviewCreate, InterviewResponse, InterviewUpdate

router = APIRouter(prefix="/interviews", tags=["Interviews"])

@router.post("", response_model=InterviewResponse)
def create_interview(data: InterviewCreate, db: Session = Depends(get_db), org: Organization = Depends(get_current_organization)):
    obj = Interview(**data.model_dump(), organization_id=org.id)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("", response_model=list[InterviewResponse])
def get_interviews(db: Session = Depends(get_db), org: Organization = Depends(get_current_organization)):
    return db.query(Interview).filter(Interview.organization_id == org.id).all()

@router.get("/{id}", response_model=InterviewResponse)
def get_interview(id: str, db: Session = Depends(get_db), org: Organization = Depends(get_current_organization)):
    obj = db.query(Interview).filter(Interview.id == id, Interview.organization_id == org.id).first()
    if not obj: raise HTTPException(status_code=404)
    return obj

@router.patch("/{id}", response_model=InterviewResponse)
def update_interview(id: str, data: InterviewUpdate, db: Session = Depends(get_db), org: Organization = Depends(get_current_organization)):
    obj = db.query(Interview).filter(Interview.id == id, Interview.organization_id == org.id).first()
    if not obj: raise HTTPException(status_code=404)
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{id}")
def delete_interview(id: str, db: Session = Depends(get_db), org: Organization = Depends(get_current_organization)):
    obj = db.query(Interview).filter(Interview.id == id, Interview.organization_id == org.id).first()
    if not obj: raise HTTPException(status_code=404)
    db.delete(obj)
    db.commit()
    return {"success": True}
