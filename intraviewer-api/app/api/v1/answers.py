from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_organization
from app.models.organization import Organization
from app.models.answer import Answer
from app.schemas.all import AnswerCreate, AnswerResponse

router = APIRouter(tags=["Answers"])

@router.post("/sessions/{id}/answers", response_model=AnswerResponse)
def create_answer(id: str, data: AnswerCreate, db: Session = Depends(get_db), org: Organization = Depends(get_current_organization)):
    obj = Answer(**data.model_dump(), session_id=id, organization_id=org.id)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/sessions/{id}/answers", response_model=list[AnswerResponse])
def get_answers(id: str, db: Session = Depends(get_db), org: Organization = Depends(get_current_organization)):
    return db.query(Answer).filter(Answer.session_id == id, Answer.organization_id == org.id).all()
