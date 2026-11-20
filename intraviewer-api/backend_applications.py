import os

MODELS_DIR = "app/models"
SCHEMAS_DIR = "app/schemas"
ROUTES_DIR = "app/api/routes"

application_model = """
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime, timezone
import uuid

def utc_now():
    return datetime.now(timezone.utc)

class Application(Base):
    __tablename__ = "applications"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    candidate_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    resume_filename = Column(String(255), nullable=True)
    resume_text = Column(Text, nullable=True)
    match_score = Column(Integer, default=0)
    match_analysis = Column(Text, nullable=True) # JSON reasoning
    status = Column(String(50), default="APPLIED") # APPLIED, SHORTLISTED, REJECTED, INTERVIEW_SCHEDULED
    created_at = Column(DateTime(timezone=True), default=utc_now)
    
    job = relationship("Job")
    candidate = relationship("User")
"""

app_routes = """
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
        # Dummy logic for fallback
        score = 75
        if "python" in resume_text.lower() and "python" in [s.lower() for s in required_skills]:
            score += 10
        return {
            "match_score": min(score, 100),
            "reasoning": "Fallback analysis: The candidate possesses some of the core skills."
        }
        
    client = Groq(api_key=settings.GROQ_API_KEY)
    prompt = f\"\"\"
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
    \"\"\"
    
    try:
        res = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
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
        return {"match_score": 60, "reasoning": "Failed to analyze fully due to error."}

@router.post("/candidate/jobs/{job_id}/apply")
async def apply_to_job(job_id: str, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(require_candidate)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job or job.status != "PUBLISHED":
        raise ApiError(404, "Job is not available for applications.")
        
    # Check if already applied
    existing = db.query(Application).filter(Application.job_id == job_id, Application.candidate_id == current_user.id).first()
    if existing:
        raise ApiError(400, "You have already applied to this job.")
        
    content = await file.read()
    raw_text = ""
    if file.filename.endswith(".pdf"):
        try:
            reader = PyPDF2.PdfReader(io.BytesIO(content))
            raw_text = "\\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
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
    
    # Calculate match
    match_result = analyze_resume_match(raw_text, jd.raw_text, skills)
    score = match_result["match_score"]
    
    threshold = blueprint.similarity_threshold or 65
    status = "SHORTLISTED" if score >= threshold else "REJECTED"
    
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
        
    apps = db.query(Application, User).join(User, Application.candidate_id == User.id).filter(Application.job_id == job_id).order_by(desc(Application.match_score)).all()
    
    res = []
    for app, candidate in apps:
        analysis = json.loads(app.match_analysis) if app.match_analysis else {}
        res.append({
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
"""

with open(f"{MODELS_DIR}/application.py", "w") as f:
    f.write(application_model)

with open(f"{MODELS_DIR}/__init__.py", "a") as f:
    f.write("\nfrom app.models.application import Application\n")

with open(f"{ROUTES_DIR}/applications.py", "w") as f:
    f.write(app_routes)

print("Backend files generated")
