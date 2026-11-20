
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.core.database import get_db
from app.api.deps import require_candidate, require_company
from app.models.user import User
from app.models.job import Job
from app.models.job_description import JobDescription
from app.models.jd_analysis import JdAnalysis
from app.models.interview_blueprint import InterviewBlueprint
from app.models.application import Application
from app.core.errors import ok, ApiError
from app.core.config import settings
from groq import Groq
import json
import io
import PyPDF2
import docx2txt

router = APIRouter(tags=["Applications"])

def analyze_resume_match(resume_text: str, jd_text: str, required_skills: list) -> dict:
    if not settings.GROQ_API_KEY:
        raise Exception("GROQ_API_KEY is not set.")
        
    client = Groq(api_key=settings.GROQ_API_KEY)
    prompt = f"""
    You are an expert technical recruiter AI.
    Compare the candidate's resume with the Job Description and provide a matching score (0-100).
    
    Job Description:
    {jd_text}
    
    Required Skills: {', '.join(required_skills)}
    
    Candidate Resume:
    {resume_text}
    
    Return EXACTLY this JSON structure:
    {{
      "match_score": int (0-100),
      "reasoning": "brief string explaining why"
    }}
    """
    
    try:
        res = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="openai/gpt-oss-120b",
            response_format={"type": "json_object"},
            temperature=0.1
        )
        data = json.loads(res.choices[0].message.content)
        return {
            "match_score": data.get("match_score", 0),
            "reasoning": data.get("reasoning", "Analysis complete.")
        }
    except Exception as e:
        print("AI Match Error:", e)
        raise ApiError(500, f"AI Analysis failed: {str(e)}")

@router.post("/candidate/jobs/{job_id}/apply")
async def apply_to_job(job_id: str, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(require_candidate)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job or job.status != "PUBLISHED":
        raise ApiError(404, "Job is not available for applications.")
        
    existing = db.query(Application).filter(Application.job_id == job_id, Application.candidate_id == current_user.id).first()
    if existing and existing.status in ["SHORTLISTED", "INTERVIEW_SCHEDULED"]:
        raise ApiError(400, "You have already been shortlisted for this job.")
        
    content = await file.read()
    raw_text = ""
    if file.filename.endswith(".pdf"):
        try:
            reader = PyPDF2.PdfReader(io.BytesIO(content))
            raw_text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        except Exception:
            raise ApiError(400, "Could not extract text from PDF.")
    elif file.filename.endswith(".docx"):
        try:
            raw_text = docx2txt.process(io.BytesIO(content))
        except Exception:
            raise ApiError(400, "Could not extract text from DOCX.")
    elif file.filename.endswith(".txt"):
        raw_text = content.decode("utf-8")
    else:
        raise ApiError(400, "Unsupported file format. Please upload PDF, DOCX, or TXT.")
        
    jd = db.query(JobDescription).filter(JobDescription.job_id == job_id).first()
    analysis = db.query(JdAnalysis).filter(JdAnalysis.job_id == job_id).first()
    blueprint = db.query(InterviewBlueprint).filter(InterviewBlueprint.job_id == job_id).first()
    
    if not jd or not analysis or not blueprint:
        raise ApiError(500, "Job data is incomplete on the server.")
        
    skills = json.loads(analysis.required_skills) if analysis.required_skills else []
    
    match_result = analyze_resume_match(raw_text, jd.raw_text, skills)
    score = match_result["match_score"]
    
    threshold = blueprint.similarity_threshold or 65
    status = "SHORTLISTED" if score >= threshold else "REJECTED"
    
    if existing:
        existing.resume_filename = file.filename
        existing.resume_text = raw_text
        existing.match_score = score
        existing.match_analysis = json.dumps(match_result)
        existing.status = status
    else:
        app = Application(
            job_id=job_id,
            candidate_id=current_user.id,
            resume_filename=file.filename,
            resume_text=raw_text,
            match_score=score,
            match_analysis=json.dumps(match_result),
            status=status
        )
        db.add(app)
        
    db.commit()
    
    return ok("Application processed", {
        "score": score,
        "threshold": threshold,
        "status": status,
        "reasoning": match_result["reasoning"]
    })

@router.get("/candidate/applications")
def get_my_applications(db: Session = Depends(get_db), current_user: User = Depends(require_candidate)):
    apps = db.query(Application).filter(Application.candidate_id == current_user.id).order_by(desc(Application.created_at)).all()
    res = []
    for app in apps:
        job = db.query(Job).filter(Job.id == app.job_id).first()
        res.append({
            "id": app.id,
            "job_id": app.job_id,
            "job_title": job.title if job else "Unknown",
            "match_score": app.match_score,
            "status": app.status,
            "created_at": str(app.created_at)
        })
    return ok("My applications", {"applications": res})

@router.get("/company/jobs/{job_id}/applications")
def get_job_applications(job_id: str, db: Session = Depends(get_db), current_company: User = Depends(require_company)):
    job = db.query(Job).filter(Job.id == job_id, Job.company_id == current_company.id).first()
    if not job:
        raise ApiError(404, "Job not found")
        
    from app.models.interview_session import InterviewSession
    apps = db.query(Application, User).join(User, Application.candidate_id == User.id).filter(Application.job_id == job_id).order_by(desc(Application.match_score)).all()
    
    res = []
    for app, candidate in apps:
        session = db.query(InterviewSession).filter(InterviewSession.application_id == app.id).first()
        session_data = None
        if session:
            session_data = {
                "status": session.status,
                "evaluation_score": session.evaluation_score,
                "integrity_score": session.integrity_score,
                "proctoring_logs": json.loads(session.proctoring_logs) if session.proctoring_logs else [],
                "transcript": json.loads(session.transcript) if session.transcript else [],
                "evaluation_details": json.loads(session.evaluation_details) if session.evaluation_details else {}
            }
            
        analysis = json.loads(app.match_analysis) if app.match_analysis else {}
        res.append({
            "session": session_data,
            "id": app.id,
            "candidate_name": candidate.name,
            "candidate_email": candidate.email,
            "resume_filename": app.resume_filename,
            "match_score": app.match_score,
            "reasoning": analysis.get("reasoning", ""),
            "status": app.status,
            "created_at": str(app.created_at)
        })
    return ok("Applications", {"applications": res})
