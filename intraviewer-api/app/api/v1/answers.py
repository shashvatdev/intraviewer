import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.answer import Answer
from app.models.interview_session import InterviewSession
from app.models.interview import Interview
from app.schemas.all import AnswerCreate
from app.services.ai.evaluation_service import evaluate_and_next_question

router = APIRouter(tags=["Answers"])

@router.post("/sessions/{id}/answers")
def create_answer(id: str, data: AnswerCreate, db: Session = Depends(get_db)):
    session = db.query(InterviewSession).filter(InterviewSession.id == id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status != "in_progress":
        raise HTTPException(status_code=400, detail="Interview is not in progress")
        
    interview = db.query(Interview).filter(Interview.id == session.interview_id).first()
    if interview and interview.duration_minutes and session.started_at:
        elapsed = datetime.datetime.now(datetime.timezone.utc) - session.started_at.replace(tzinfo=datetime.timezone.utc)
        if elapsed.total_seconds() > interview.duration_minutes * 60:
            session.status = "completed"
            db.commit()
            raise HTTPException(status_code=400, detail="Time limit exceeded")

    existing = db.query(Answer).filter(Answer.question_id == data.question_id, Answer.session_id == id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Question already answered")

    ans = Answer(
        session_id=id, 
        question_id=data.question_id, 
        organization_id=session.organization_id, 
        text_answer=data.text_answer
    )
    db.add(ans)
    db.commit()
    db.refresh(ans)
    
    result = evaluate_and_next_question(db, ans.id)
    
    next_q = result.get("next_question")
    return {
        "score": result["evaluation"]["score"],
        "feedback": result["evaluation"]["feedback"],
        "next_question": {
            "id": next_q.id,
            "text": next_q.text
        } if next_q else None
    }

@router.get("/sessions/{id}/answers")
def get_answers(id: str, db: Session = Depends(get_db)):
    # Making this public to candidate as well for now or can restrict back to recruiter.
    return db.query(Answer).filter(Answer.session_id == id).all()
