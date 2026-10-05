from fastapi import APIRouter, Depends
from app.schemas.all import AIBlueprintRequest, AIGenerateQuestionsRequest, AIEvaluateAnswerRequest, AIEvaluateInterviewRequest
from app.core.security import get_current_organization
from app.models.organization import Organization

router = APIRouter(prefix="/ai", tags=["AI Services"])

@router.post("/interview-blueprint")
def create_blueprint(data: AIBlueprintRequest, org: Organization = Depends(get_current_organization)):
    return {"blueprint": f"Mock blueprint for {data.job_title}"}

@router.post("/generate-questions")
def generate_questions(data: AIGenerateQuestionsRequest, org: Organization = Depends(get_current_organization)):
    return {"questions": [{"text": "Mock question 1"}, {"text": "Mock question 2"}]}

@router.post("/evaluate-answer")
def evaluate_answer(data: AIEvaluateAnswerRequest, org: Organization = Depends(get_current_organization)):
    return {"score": 8.5, "feedback": "Good answer"}

@router.post("/evaluate-interview")
def evaluate_interview(data: AIEvaluateInterviewRequest, org: Organization = Depends(get_current_organization)):
    return {"overall_score": 9.0, "summary": "Great interview"}
