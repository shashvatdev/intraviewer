from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_organization
from app.models.organization import Organization
from app.models.evaluation import Evaluation
from app.schemas.all import EvaluationCreate, EvaluationResponse

router = APIRouter(tags=["Evaluations"])

@router.post("/sessions/{id}/evaluate", response_model=EvaluationResponse)
def create_evaluation(id: str, data: EvaluationCreate, db: Session = Depends(get_db), org: Organization = Depends(get_current_organization)):
    obj = Evaluation(**data.model_dump(), session_id=id, organization_id=org.id)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/sessions/{id}/evaluation")
def get_evaluation(id: str, db: Session = Depends(get_db), org: Organization = Depends(get_current_organization)):
    obj = db.query(Evaluation).filter(Evaluation.session_id == id, Evaluation.organization_id == org.id).first()
    if not obj: raise HTTPException(status_code=404)
    return {
        "overall_score": obj.overall_score,
        "recommendation": obj.recommendation,
        "technical_score": obj.technical_score,
        "communication_score": obj.communication_score,
        "strengths": obj.strengths,
        "weaknesses": obj.weaknesses,
        "final_report": obj.final_report
    }
