from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_organization
from app.models.organization import Organization
from app.schemas.ai import AIBlueprintRequest, AIGenerateQuestionsRequest, AIEvaluateAnswerRequest, AIEvaluateInterviewRequest
from app.services.ai.blueprint_service import generate_blueprint
from app.services.ai.question_service import generate_questions
from app.services.ai.evaluation_service import evaluate_and_next_question, evaluate_interview

router = APIRouter(prefix="/ai", tags=["AI Services"])

@router.post("/interview-blueprint")
def create_blueprint(data: AIBlueprintRequest, db: Session = Depends(get_db), org: Organization = Depends(get_current_organization)):
    try:
        return generate_blueprint(db, data.interview_id, data.job_description, data.skills, data.difficulty, data.duration_minutes)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/generate-questions")
def create_questions(data: AIGenerateQuestionsRequest, db: Session = Depends(get_db), org: Organization = Depends(get_current_organization)):
    try:
        return generate_questions(db, data.interview_id, data.count)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/evaluate-answer")
def evaluate_answer(data: AIEvaluateAnswerRequest, db: Session = Depends(get_db), org: Organization = Depends(get_current_organization)):
    try:
        return evaluate_and_next_question(db, data.answer_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/evaluate-interview")
def evaluate_session(data: AIEvaluateInterviewRequest, db: Session = Depends(get_db), org: Organization = Depends(get_current_organization)):
    try:
        return evaluate_interview(db, data.session_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
