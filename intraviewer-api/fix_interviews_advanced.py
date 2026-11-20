import os
import json

ROUTES_DIR = "app/api/routes"

code = """
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import require_candidate
from app.models.user import User
from app.models.application import Application
from app.models.job import Job
from app.models.interview_blueprint import InterviewBlueprint
from app.models.interview_session import InterviewSession
from app.core.errors import ok, ApiError
from app.core.config import settings
from pydantic import BaseModel
import json
import base64
import asyncio
from datetime import datetime, timezone
from groq import Groq
import edge_tts
import tempfile
import os

router = APIRouter(tags=["Interviews"])

class MessageRequest(BaseModel):
    message: str = ""
    audio_base64: str = None

def get_tts_sync(text: str) -> str:
    \"\"\"Generates TTS using edge-tts synchronously and returns base64 audio.\"\"\"
    async def _generate():
        communicate = edge_tts.Communicate(text, "en-US-JennyNeural")
        tmp_path = tempfile.mktemp(suffix=".mp3")
        await communicate.save(tmp_path)
        with open(tmp_path, "rb") as f:
            data = f.read()
        os.remove(tmp_path)
        return base64.b64encode(data).decode("utf-8")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(_generate())
    loop.close()
    return result

def transcribe_audio_sync(audio_base64: str) -> str:
    \"\"\"Transcribes audio using Groq Whisper.\"\"\"
    client = Groq(api_key=settings.GROQ_API_KEY)
    tmp_path = tempfile.mktemp(suffix=".webm")
    try:
        with open(tmp_path, "wb") as f:
            f.write(base64.b64decode(audio_base64))
        
        with open(tmp_path, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(tmp_path, file.read()),
                model="whisper-large-v3",
                response_format="text"
            )
        os.remove(tmp_path)
        return transcription
    except Exception as e:
        print("Whisper Error:", e)
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        return ""

@router.post("/applications/{application_id}/start-interview")
def start_interview(application_id: str, db: Session = Depends(get_db), current_user: User = Depends(require_candidate)):
    app = db.query(Application).filter(Application.id == application_id, Application.candidate_id == current_user.id).first()
    if not app:
        raise ApiError(404, "Application not found")
        
    existing = db.query(InterviewSession).filter(InterviewSession.application_id == application_id).first()
    if existing:
        return ok("Interview session retrieved", {"session_id": existing.id})
        
    session = InterviewSession(
        application_id=application_id,
        status="SCHEDULED",
        transcript=json.dumps([]),
        evaluation_details=json.dumps({"stage": "GREETING", "ai_prob": 0, "logistics_responses": {}})
    )
    db.add(session)
    db.commit()
    
    return ok("Interview session created", {"session_id": session.id})

@router.get("/interviews/{session_id}")
def get_interview(session_id: str, db: Session = Depends(get_db)):
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise ApiError(404, "Interview session not found")
        
    app = db.query(Application).filter(Application.id == session.application_id).first()
    job = db.query(Job).filter(Job.id == app.job_id).first()
    candidate = db.query(User).filter(User.id == app.candidate_id).first()
    
    return ok("Session details", {
        "status": session.status,
        "job_title": job.title if job else "Role",
        "company_name": "Company",
        "candidate_name": candidate.name if candidate else "Candidate",
        "transcript": json.loads(session.transcript) if session.transcript else []
    })

@router.post("/interviews/{session_id}/message")
def send_message(session_id: str, payload: MessageRequest, db: Session = Depends(get_db)):
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise ApiError(404, "Session not found")
        
    if session.status == "COMPLETED":
        raise ApiError(400, "Interview already completed")
        
    if session.status == "SCHEDULED":
        session.status = "IN_PROGRESS"
        session.started_at = datetime.now(timezone.utc)
        
    transcript = json.loads(session.transcript) if session.transcript else []
    eval_details = json.loads(session.evaluation_details) if session.evaluation_details else {"stage": "GREETING", "ai_prob": 0, "logistics_responses": {}}
    
    app = db.query(Application).filter(Application.id == session.application_id).first()
    job = db.query(Job).filter(Job.id == app.job_id).first()
    candidate = db.query(User).filter(User.id == app.candidate_id).first()
    
    user_text = payload.message
    if payload.audio_base64:
        user_text = transcribe_audio_sync(payload.audio_base64)
        print("Transcribed:", user_text)
    
    if user_text.strip():
        transcript.append({"role": "user", "content": user_text.strip()})
        
    client = Groq(api_key=settings.GROQ_API_KEY)
    
    system_prompt = f\"\"\"
You are Alex, an expert AI Technical Recruiter conducting an interview with {candidate.name} for the role of {job.title}.

CRITICAL RULES:
1. If the user's message is empty, gibberish, or sounds like a mic test ("hello 1 2 3"), set `unclear_audio` to true and ask them to speak louder and clearer without penalizing them.
2. If `unclear_audio` is true, repeat the previous question naturally.
3. Detect if the user sounds like they are reading from ChatGPT. Update `ai_cheating_probability`.
4. Always respond in STRICT JSON.

CURRENT STAGE: {eval_details.get('stage')}

INTERVIEW PROGRESSION:
- GREETING: Greet {candidate.name}, explain rules ("no tab switching, look at the camera"). Ask if they understood. Next stage: INTRODUCTION.
- INTRODUCTION: Ask them to introduce themselves. Next: LOGISTICS.
- LOGISTICS: Ask if they are willing to relocate and comfortable with work hours. Keep these details out of technical rating. Next: RESUME.
- RESUME: Ask 1-2 generic questions about their projects/experience based on their resume. Match difficulty to job. Next: TECHNICAL.
- TECHNICAL: Ask a real-world problem scenario. Next: ENDING when done or if performing poorly.
- ENDING: Say EXACTLY "Thank you for your time. This concludes our interview. The team will review your responses and get back to you shortly. Have a wonderful day!" Set `is_completed` to true.

CANDIDATE RESUME: {app.resume_text[:1500] if app.resume_text else ""}

JSON FORMAT:
{{
  "spoken_response": "What you actually say",
  "next_stage": "GREETING | INTRODUCTION | LOGISTICS | RESUME | TECHNICAL | ENDING",
  "is_completed": boolean,
  "unclear_audio": boolean,
  "technical_score": int (0-100),
  "ai_cheating_probability": int (0-100)
}}
\"\"\"
    
    messages = [{"role": "system", "content": system_prompt}]
    for msg in transcript[-6:]: # Keep context manageable
        messages.append({"role": msg["role"], "content": msg["content"]})
        
    try:
        res = client.chat.completions.create(
            messages=messages,
            model="openai/gpt-oss-120b",
            response_format={"type": "json_object"},
            temperature=0.3
        )
        data = json.loads(res.choices[0].message.content)
        
        ai_response = data.get("spoken_response", "Let's continue.")
        is_completed = data.get("is_completed", False)
        
        eval_details["stage"] = data.get("next_stage", eval_details.get("stage"))
        eval_details["ai_prob"] = data.get("ai_cheating_probability", 0)
            
        if data.get("technical_score"):
            session.evaluation_score = data.get("technical_score")
            
        session.evaluation_details = json.dumps(eval_details)
        
        if is_completed:
            session.status = "COMPLETED"
            session.completed_at = datetime.now(timezone.utc)
            
        transcript.append({"role": "assistant", "content": ai_response})
        session.transcript = json.dumps(transcript)
        db.commit()
        
        audio_base64 = get_tts_sync(ai_response)
        
        return ok("Message processed", {
            "response": ai_response,
            "is_completed": is_completed,
            "unclear_audio": data.get("unclear_audio", False),
            "audio_base64": audio_base64,
            "user_transcribed_text": user_text
        })
    except Exception as e:
        print("Interview Error:", e)
        # Fallback
        ai_response = "I'm having a little trouble connecting to my processing core. Could you repeat that?"
        audio_base64 = get_tts_sync(ai_response)
        return ok("Message processed", {
            "response": ai_response,
            "is_completed": False,
            "unclear_audio": True,
            "audio_base64": audio_base64,
            "user_transcribed_text": user_text
        })

@router.post("/interviews/{session_id}/proctoring-event")
def log_proctoring_event(session_id: str, payload: dict, db: Session = Depends(get_db)):
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise ApiError(404, "Session not found")
        
    logs = json.loads(session.proctoring_logs) if session.proctoring_logs else []
    
    logs.append({
        "timestamp": str(datetime.now(timezone.utc)),
        "type": payload.get("event_type"),
        "description": payload.get("description")
    })
    
    deductions = {
        "TAB_SWITCH": 33, # 3 strikes = 100
    }
    
    penalty = deductions.get(payload.get("event_type"), 0)
    current_score = session.integrity_score if session.integrity_score is not None else 100
    session.integrity_score = max(0, current_score - penalty)
    
    session.proctoring_logs = json.dumps(logs)
    db.commit()
    
    return ok("Event logged", {"integrity_score": session.integrity_score})
"""
with open(f"{ROUTES_DIR}/interviews.py", "w") as f:
    f.write(code)
    
print("Updated backend for EdgeTTS & VAD STT support")
