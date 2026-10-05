from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_organization
from app.models.organization import Organization
from app.models.question import Question
from app.schemas.all import QuestionCreate, QuestionResponse, QuestionUpdate

router = APIRouter(tags=["Questions"])

@router.post("/interviews/{id}/questions", response_model=QuestionResponse)
def create_question(id: str, data: QuestionCreate, db: Session = Depends(get_db), org: Organization = Depends(get_current_organization)):
    obj = Question(**data.model_dump(), interview_id=id, organization_id=org.id)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/interviews/{id}/questions", response_model=list[QuestionResponse])
def get_questions(id: str, db: Session = Depends(get_db), org: Organization = Depends(get_current_organization)):
    return db.query(Question).filter(Question.interview_id == id, Question.organization_id == org.id).all()

@router.patch("/questions/{id}", response_model=QuestionResponse)
def update_question(id: str, data: QuestionUpdate, db: Session = Depends(get_db), org: Organization = Depends(get_current_organization)):
    obj = db.query(Question).filter(Question.id == id, Question.organization_id == org.id).first()
    if not obj: raise HTTPException(status_code=404)
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/questions/{id}")
def delete_question(id: str, db: Session = Depends(get_db), org: Organization = Depends(get_current_organization)):
    obj = db.query(Question).filter(Question.id == id, Question.organization_id == org.id).first()
    if not obj: raise HTTPException(status_code=404)
    db.delete(obj)
    db.commit()
    return {"success": True}
