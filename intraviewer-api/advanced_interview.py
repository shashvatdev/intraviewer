import os
import json

ROUTES_DIR = "app/api/routes"

new_routes = """
from fastapi import APIRouter, Depends, HTTPException
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
from datetime import datetime, timezone
from groq import Groq

router = APIRouter(tags=["Interviews"])

class MessageRequest(BaseModel):
    message: str

@router.post("/applications/{application_id}/start-interview")
def start_interview(application_id: str, db: Session = Depends(get_db), current_user: User = Depends(require_candidate)):
    app = db.query(Application).filter(Application.id == application_id, Application.candidate_id == current_user.id).first()
    if not app:
        raise ApiError(404, "Application not found")
        
    if app.status != "SHORTLISTED":
        raise ApiError(400, "Only shortlisted candidates can start the interview")
        
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
    
    if payload.message:
        transcript.append({"role": "user", "content": payload.message})
        
    if not settings.GROQ_API_KEY:
        raise Exception("GROQ_API_KEY is not set.")
        
    client = Groq(api_key=settings.GROQ_API_KEY)
    
    system_prompt = f\"\"\"
You are Alex, an expert AI Technical Recruiter conducting an interview with {candidate.name} for the role of {job.title}.
Your responses will be spoken aloud to the candidate via Text-to-Speech, so keep them conversational, natural, and concise.

CRITICAL RULES FOR YOU TO FOLLOW:
1. If the user's message is empty/gibberish, ask them to repeat and state you couldn't hear them properly.
2. Determine if the user's answer sounds like it was copy-pasted from ChatGPT (AI generated). Update `ai_cheating_probability` (0-100).
3. Do not stretch the interview unnecessarily. If they are performing very poorly, wrap up the interview gracefully.
4. Always respond in strictly valid JSON format.

CURRENT STAGE: {eval_details.get('stage')}

INTERVIEW PROGRESSION (Move through these stages naturally based on candidate's answers):
- GREETING: Greet {candidate.name}, explain rules ("no tab switching, look at the camera, dual face detection is active"). Ask if they understood. If they say yes, transition stage to INTRODUCTION.
- INTRODUCTION: Ask them to introduce themselves. Transition to LOGISTICS.
- LOGISTICS: Ask if they are willing to relocate (Job location: {job.location}) and comfortable with work hours. Keep these details out of technical rating. Transition to RESUME.
- RESUME: Ask 1-2 generic questions about their projects/experience based on their resume. Difficulty should match the job requirements (Fresher = easy, Senior = hard). Transition to TECHNICAL.
- TECHNICAL: Ask a real-world problem scenario. You don't need a perfect answer, just test if their thinking is technical. Transition to ENDING when done or if they perform poorly.
- ENDING: Provide a proper ending note. "Your result will be announced soon." Set `is_completed` to true.

CANDIDATE RESUME:
{app.resume_text[:2000] if app.resume_text else "No resume text available."}

JSON RESPONSE FORMAT:
{{
  "spoken_response": "What you actually say to the candidate",
  "next_stage": "GREETING | INTRODUCTION | LOGISTICS | RESUME | TECHNICAL | ENDING",
  "is_completed": boolean,
  "technical_score": int (0-100, update as you ask tech questions),
  "ai_cheating_probability": int (0-100, estimate how much they sound like a bot),
  "logistics_notes": "Brief note on relocation/hours if discussed"
}}
\"\"\"
    
    # Build messages for LLM
    messages = [{"role": "system", "content": system_prompt}]
    for msg in transcript:
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
        
        if "logistics_notes" in data and data["logistics_notes"]:
            eval_details["logistics_responses"] = data["logistics_notes"]
            
        if data.get("technical_score"):
            session.evaluation_score = data.get("technical_score")
            
        session.evaluation_details = json.dumps(eval_details)
        
        if is_completed:
            session.status = "COMPLETED"
            session.completed_at = datetime.now(timezone.utc)
            
        transcript.append({"role": "assistant", "content": ai_response})
        session.transcript = json.dumps(transcript)
        db.commit()
        
        return ok("Message processed", {
            "response": ai_response,
            "is_completed": is_completed
        })
    except Exception as e:
        print("Interview LLM Error:", e)
        # Fallback to prevent breaking the flow entirely
        ai_response = "I'm having a little trouble connecting to my processing core. Could you repeat that?"
        transcript.append({"role": "assistant", "content": ai_response})
        session.transcript = json.dumps(transcript)
        db.commit()
        return ok("Message processed", {
            "response": ai_response,
            "is_completed": False
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
        "TAB_SWITCH": 10,
        "MULTIPLE_FACES": 15,
        "NO_FACE": 5,
        "LOOKING_AWAY": 2,
        "COPY_PASTE": 5
    }
    
    penalty = deductions.get(payload.get("event_type"), 0)
    current_score = session.integrity_score if session.integrity_score is not None else 100
    session.integrity_score = max(0, current_score - penalty)
    
    session.proctoring_logs = json.dumps(logs)
    db.commit()
    
    return ok("Event logged", {"integrity_score": session.integrity_score})
"""
with open(f"{ROUTES_DIR}/interviews.py", "w") as f:
    f.write(new_routes)
    
print("Updated advanced interview AI flow")
