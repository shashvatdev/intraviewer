import datetime
import shutil
import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.interview_session import InterviewSession
from app.models.question import Question
from app.models.answer import Answer
from app.models.interview import Interview
from app.services.ai.tts_service import generate_tts
from app.services.ai.stt_service import transcribe_audio
from app.services.ai.evaluation_service import evaluate_and_next_question

router = APIRouter(tags=["Voice Interview"])

@router.post("/public/interviews/{token}/voice/start")
def start_voice_interview(token: str, db: Session = Depends(get_db)):
    session = db.query(InterviewSession).filter(InterviewSession.public_token == token).first()
    if not session: raise HTTPException(status_code=404, detail="Session not found")
    if session.status != "pending": raise HTTPException(status_code=400, detail="Interview already started or completed")
    
    session.status = "in_progress"
    session.started_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(session)
    
    question = db.query(Question).filter(
        Question.interview_id == session.interview_id,
        Question.is_dynamic == False
    ).order_by(Question.id).first()
    
    audio_url = None
    if question:
        audio_url = generate_tts(question.text, question.id)
    
    return {
        "session_id": session.id,
        "question_id": question.id if question else None,
        "question": question.text if question else None,
        "audio_url": audio_url
    }

@router.post("/sessions/{session_id}/voice-answer")
def submit_voice_answer(
    session_id: str, 
    question_id: str = Form(...),
    audio: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status != "in_progress":
        raise HTTPException(status_code=400, detail="Interview is not in progress")
        
    # Check duration limit
    interview = db.query(Interview).filter(Interview.id == session.interview_id).first()
    if interview and interview.duration_minutes and session.started_at:
        elapsed = datetime.datetime.now(datetime.timezone.utc) - session.started_at.replace(tzinfo=datetime.timezone.utc)
        if elapsed.total_seconds() > interview.duration_minutes * 60:
            session.status = "completed"
            db.commit()
            raise HTTPException(status_code=400, detail="Time limit exceeded")

    # Duplicate check
    existing = db.query(Answer).filter(Answer.question_id == question_id, Answer.session_id == session_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Question already answered")

    # Save audio temporarily
    temp_filename = f"temp_{uuid.uuid4()}.mp3"
    temp_path = os.path.join("app", "static", "audio", temp_filename)
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)
        
    try:
        # 1. STT
        transcript = transcribe_audio(temp_path)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    # 2. Save Answer
    ans = Answer(
        session_id=session_id, 
        question_id=question_id, 
        organization_id=session.organization_id, 
        text_answer=transcript
    )
    db.add(ans)
    db.commit()
    db.refresh(ans)
    
    # 3. Evaluate & Next Question
    result = evaluate_and_next_question(db, ans.id)
    next_q = result.get("next_question")
    
    # 4. TTS for next question
    next_audio_url = None
    if next_q:
        next_audio_url = generate_tts(next_q.text, next_q.id)
    
    return {
        "transcript": transcript,
        "score": result["evaluation"]["score"],
        "feedback": result["evaluation"]["feedback"],
        "next_question": {
            "id": next_q.id,
            "text": next_q.text
        } if next_q else None,
        "audio_url": next_audio_url
    }
