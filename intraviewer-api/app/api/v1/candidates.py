from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_organization
from app.models.organization import Organization
from app.models.candidate import Candidate
from app.schemas.all import CandidateCreate, CandidateResponse, CandidateUpdate

router = APIRouter(prefix="/candidates", tags=["Candidates"])

@router.post("", response_model=CandidateResponse)
def create_candidate(data: CandidateCreate, db: Session = Depends(get_db), org: Organization = Depends(get_current_organization)):
    obj = Candidate(**data.model_dump(), organization_id=org.id)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("", response_model=list[CandidateResponse])
def get_candidates(db: Session = Depends(get_db), org: Organization = Depends(get_current_organization)):
    return db.query(Candidate).filter(Candidate.organization_id == org.id).all()

@router.get("/{id}", response_model=CandidateResponse)
def get_candidate(id: str, db: Session = Depends(get_db), org: Organization = Depends(get_current_organization)):
    obj = db.query(Candidate).filter(Candidate.id == id, Candidate.organization_id == org.id).first()
    if not obj: raise HTTPException(status_code=404)
    return obj

@router.patch("/{id}", response_model=CandidateResponse)
def update_candidate(id: str, data: CandidateUpdate, db: Session = Depends(get_db), org: Organization = Depends(get_current_organization)):
    obj = db.query(Candidate).filter(Candidate.id == id, Candidate.organization_id == org.id).first()
    if not obj: raise HTTPException(status_code=404)
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj
