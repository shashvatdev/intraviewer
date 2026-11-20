import os
import sys

# Define files to create
MODELS_DIR = "app/models"
SCHEMAS_DIR = "app/schemas"
SERVICES_DIR = "app/services"
ROUTES_DIR = "app/api/routes"

job_model = """
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Float, Text, Enum
from sqlalchemy.orm import relationship
import enum
from app.db.base import Base
from datetime import datetime, timezone
import uuid

def utc_now():
    return datetime.now(timezone.utc)

class JobStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    PAUSED = "PAUSED"
    EXPIRED = "EXPIRED"
    CLOSED = "CLOSED"

class Job(Base):
    __tablename__ = "jobs"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    department = Column(String(255), nullable=True)
    ctc_type = Column(String(50), nullable=True)
    ctc_min = Column(String(50), nullable=True)
    ctc_max = Column(String(50), nullable=True)
    currency = Column(String(20), default="INR")
    work_start_time = Column(String(20), nullable=True)
    work_end_time = Column(String(20), nullable=True)
    timezone = Column(String(50), nullable=True)
    shift_type = Column(String(50), nullable=True)
    work_mode = Column(String(50), nullable=True)
    location = Column(String(255), nullable=True)
    relocation_required = Column(Boolean, default=False)
    deadline = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), default=JobStatus.DRAFT.value)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    
    # Relationships
    description = relationship("JobDescription", back_populates="job", uselist=False, cascade="all, delete-orphan")
    analysis = relationship("JdAnalysis", back_populates="job", uselist=False, cascade="all, delete-orphan")
    blueprint = relationship("InterviewBlueprint", back_populates="job", uselist=False, cascade="all, delete-orphan")
"""

job_desc_model = """
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime, timezone
import uuid

def utc_now():
    return datetime.now(timezone.utc)

class JobDescription(Base):
    __tablename__ = "job_descriptions"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), unique=True)
    source_type = Column(String(50), nullable=False) # PDF, DOCX, TXT, RICH_TEXT
    original_filename = Column(String(255), nullable=True)
    raw_text = Column(Text, nullable=False)
    structured_text = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    
    job = relationship("Job", back_populates="description")
"""

jd_analysis_model = """
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime, timezone
import uuid

def utc_now():
    return datetime.now(timezone.utc)

class JdAnalysis(Base):
    __tablename__ = "jd_analysis"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), unique=True)
    required_skills = Column(Text, nullable=True) # JSON
    good_to_have_skills = Column(Text, nullable=True) # JSON
    hard_requirements = Column(Text, nullable=True) # JSON
    preferred_requirements = Column(Text, nullable=True) # JSON
    minimum_experience = Column(Integer, nullable=True)
    maximum_experience = Column(Integer, nullable=True)
    education = Column(Text, nullable=True) # JSON
    role_level = Column(String(50), nullable=True)
    domain = Column(String(100), nullable=True)
    raw_ai_response = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    
    job = relationship("Job", back_populates="analysis")
"""

blueprint_model = """
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime, timezone
import uuid

def utc_now():
    return datetime.now(timezone.utc)

class InterviewBlueprint(Base):
    __tablename__ = "interview_blueprints"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), unique=True)
    persona_level = Column(String(50), nullable=True)
    estimated_duration = Column(Integer, nullable=True)
    question_distribution = Column(Text, nullable=True) # JSON
    evaluation_weights = Column(Text, nullable=True) # JSON
    similarity_threshold = Column(Integer, default=65)
    version = Column(Integer, default=1)
    status = Column(String(50), default="DRAFT")
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    
    job = relationship("Job", back_populates="blueprint")
"""

schema_code = """
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class JobCreate(BaseModel):
    title: str
    department: Optional[str] = None
    ctc_type: Optional[str] = None
    ctc_min: Optional[str] = None
    ctc_max: Optional[str] = None
    currency: Optional[str] = "INR"
    work_start_time: Optional[str] = None
    work_end_time: Optional[str] = None
    timezone: Optional[str] = None
    shift_type: Optional[str] = None
    work_mode: Optional[str] = None
    location: Optional[str] = None
    relocation_required: Optional[bool] = False
    deadline: Optional[datetime] = None

class JobUpdate(BaseModel):
    title: Optional[str] = None
    department: Optional[str] = None
    ctc_type: Optional[str] = None
    ctc_min: Optional[str] = None
    ctc_max: Optional[str] = None
    currency: Optional[str] = None
    work_start_time: Optional[str] = None
    work_end_time: Optional[str] = None
    timezone: Optional[str] = None
    shift_type: Optional[str] = None
    work_mode: Optional[str] = None
    location: Optional[str] = None
    relocation_required: Optional[bool] = None
    deadline: Optional[datetime] = None

class ManualJdUpload(BaseModel):
    raw_text: str

class BlueprintUpdate(BaseModel):
    persona_level: Optional[str] = None
    estimated_duration: Optional[int] = None
    question_distribution: Optional[Dict[str, Any]] = None
    evaluation_weights: Optional[Dict[str, int]] = None
    similarity_threshold: Optional[int] = None
"""

ai_service_code = """
import json
import os
import re
from typing import Dict, Any

# A mock for the AI service if Groq API key is missing.
# In a real app we would use the groq SDK here.
def extract_jd_analysis(text: str) -> Dict[str, Any]:
    # Dummy logic to extract semantic details for MVP
    text_lower = text.lower()
    
    # Simple experience extraction
    exp_match = re.search(r'(\d+)\s*[-+to]*\s*(\d+)?\s*years?', text_lower)
    min_exp = int(exp_match.group(1)) if exp_match else 0
    max_exp = int(exp_match.group(2)) if exp_match and exp_match.group(2) else min_exp + 2
    
    role_level = "JUNIOR"
    if min_exp >= 3: role_level = "MID"
    if min_exp >= 6: role_level = "SENIOR"
    
    skills = []
    for s in ["python", "react", "fastapi", "sql", "aws", "docker", "node", "java"]:
        if s in text_lower: skills.append(s.title())
    
    if not skills:
        skills = ["Communication", "Problem Solving"]
        
    return {
        "required_skills": skills[:4],
        "good_to_have_skills": skills[4:],
        "hard_requirements": [f"{min_exp}+ years experience"],
        "preferred_requirements": ["Strong problem solving"],
        "minimum_experience": min_exp,
        "maximum_experience": max_exp,
        "education": ["B.Tech/BE or equivalent"],
        "role_level": role_level,
        "domain": "Engineering"
    }

def generate_blueprint(analysis: Dict[str, Any]) -> Dict[str, Any]:
    level = analysis.get("role_level", "JUNIOR")
    return {
        "persona_level": level,
        "estimated_duration": 30 if level == "SENIOR" else 20,
        "question_distribution": {
            "introduction": 1,
            "resume_deep_dive": 2,
            "technical": 4 if level == "SENIOR" else 3,
            "real_world": 2
        },
        "evaluation_weights": {
            "communication": 20,
            "technical": 50,
            "problem_solving": 30
        }
    }
"""

job_routes_code = """
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import require_company
from app.models.user import User
from app.models.job import Job, JobStatus
from app.models.job_description import JobDescription
from app.models.jd_analysis import JdAnalysis
from app.models.interview_blueprint import InterviewBlueprint
from app.schemas.job import JobCreate, JobUpdate, ManualJdUpload, BlueprintUpdate
from app.core.errors import ok, ApiError
from app.services.ai_service import extract_jd_analysis, generate_blueprint
import json
import io
import PyPDF2
import docx2txt

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post("")
def create_job(payload: JobCreate, db: Session = Depends(get_db), current_company: User = Depends(require_company)):
    job = Job(**payload.model_dump(exclude_unset=True), company_id=current_company.id)
    db.add(job)
    db.commit()
    db.refresh(job)
    return ok("Job created", {"job_id": job.id})

@router.get("")
def list_jobs(db: Session = Depends(get_db), current_company: User = Depends(require_company)):
    jobs = db.query(Job).filter(Job.company_id == current_company.id).all()
    # Simple serialization
    return ok("Jobs fetched", {"jobs": [{"id": j.id, "title": j.title, "status": j.status, "created_at": str(j.created_at)} for j in jobs]})

@router.get("/{job_id}")
def get_job(job_id: str, db: Session = Depends(get_db), current_company: User = Depends(require_company)):
    job = db.query(Job).filter(Job.id == job_id, Job.company_id == current_company.id).first()
    if not job:
        raise ApiError(404, "Job not found")
    
    desc = db.query(JobDescription).filter(JobDescription.job_id == job.id).first()
    analysis = db.query(JdAnalysis).filter(JdAnalysis.job_id == job.id).first()
    blueprint = db.query(InterviewBlueprint).filter(InterviewBlueprint.job_id == job.id).first()
    
    data = {
        "id": job.id,
        "title": job.title,
        "department": job.department,
        "ctc_min": job.ctc_min,
        "ctc_max": job.ctc_max,
        "location": job.location,
        "status": job.status,
        "has_jd": bool(desc),
        "has_analysis": bool(analysis),
        "has_blueprint": bool(blueprint)
    }
    
    if analysis:
        data["analysis"] = {
            "role_level": analysis.role_level,
            "required_skills": json.loads(analysis.required_skills) if analysis.required_skills else [],
            "preferred_requirements": json.loads(analysis.preferred_requirements) if analysis.preferred_requirements else [],
            "hard_requirements": json.loads(analysis.hard_requirements) if analysis.hard_requirements else [],
        }
        
    if blueprint:
        data["blueprint"] = {
            "id": blueprint.id,
            "estimated_duration": blueprint.estimated_duration,
            "similarity_threshold": blueprint.similarity_threshold,
            "evaluation_weights": json.loads(blueprint.evaluation_weights) if blueprint.evaluation_weights else {},
            "question_distribution": json.loads(blueprint.question_distribution) if blueprint.question_distribution else {}
        }
        
    return ok("Job details", data)

@router.post("/{job_id}/jd/upload")
async def upload_jd(job_id: str, file: UploadFile = File(...), db: Session = Depends(get_db), current_company: User = Depends(require_company)):
    job = db.query(Job).filter(Job.id == job_id, Job.company_id == current_company.id).first()
    if not job:
        raise ApiError(404, "Job not found")
        
    content = await file.read()
    raw_text = ""
    
    if file.filename.endswith(".pdf"):
        try:
            reader = PyPDF2.PdfReader(io.BytesIO(content))
            raw_text = "\\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        except Exception as e:
            raise ApiError(400, "Could not extract readable text from this PDF.")
    elif file.filename.endswith(".docx"):
        try:
            raw_text = docx2txt.process(io.BytesIO(content))
        except Exception:
            raise ApiError(400, "Could not extract text from DOCX.")
    elif file.filename.endswith(".txt"):
        raw_text = content.decode("utf-8")
    else:
        raise ApiError(400, "Unsupported file format. Please upload PDF, DOCX, or TXT.")
        
    if not raw_text.strip():
        raise ApiError(400, "We couldn't extract readable text from this file. Please paste manually.")
        
    # Delete old JD
    db.query(JobDescription).filter(JobDescription.job_id == job_id).delete()
    
    desc = JobDescription(job_id=job_id, source_type="FILE", original_filename=file.filename, raw_text=raw_text)
    db.add(desc)
    db.commit()
    return ok("JD uploaded and extracted successfully")

@router.post("/{job_id}/jd/text")
def upload_jd_text(job_id: str, payload: ManualJdUpload, db: Session = Depends(get_db), current_company: User = Depends(require_company)):
    job = db.query(Job).filter(Job.id == job_id, Job.company_id == current_company.id).first()
    if not job:
        raise ApiError(404, "Job not found")
    
    if not payload.raw_text.strip():
        raise ApiError(400, "JD text cannot be empty.")
        
    db.query(JobDescription).filter(JobDescription.job_id == job_id).delete()
    desc = JobDescription(job_id=job_id, source_type="RICH_TEXT", raw_text=payload.raw_text)
    db.add(desc)
    db.commit()
    return ok("JD saved successfully")

@router.post("/{job_id}/jd/analyze")
def analyze_jd(job_id: str, db: Session = Depends(get_db), current_company: User = Depends(require_company)):
    job = db.query(Job).filter(Job.id == job_id, Job.company_id == current_company.id).first()
    if not job:
        raise ApiError(404, "Job not found")
        
    desc = db.query(JobDescription).filter(JobDescription.job_id == job_id).first()
    if not desc:
        raise ApiError(400, "No JD found for this job")
        
    res = extract_jd_analysis(desc.raw_text)
    
    db.query(JdAnalysis).filter(JdAnalysis.job_id == job_id).delete()
    
    analysis = JdAnalysis(
        job_id=job_id,
        required_skills=json.dumps(res.get("required_skills", [])),
        good_to_have_skills=json.dumps(res.get("good_to_have_skills", [])),
        hard_requirements=json.dumps(res.get("hard_requirements", [])),
        preferred_requirements=json.dumps(res.get("preferred_requirements", [])),
        minimum_experience=res.get("minimum_experience"),
        maximum_experience=res.get("maximum_experience"),
        education=json.dumps(res.get("education", [])),
        role_level=res.get("role_level"),
        domain=res.get("domain")
    )
    db.add(analysis)
    
    # auto generate blueprint
    db.query(InterviewBlueprint).filter(InterviewBlueprint.job_id == job_id).delete()
    bp_data = generate_blueprint(res)
    bp = InterviewBlueprint(
        job_id=job_id,
        persona_level=bp_data["persona_level"],
        estimated_duration=bp_data["estimated_duration"],
        question_distribution=json.dumps(bp_data["question_distribution"]),
        evaluation_weights=json.dumps(bp_data["evaluation_weights"])
    )
    db.add(bp)
    
    db.commit()
    return ok("Analysis complete", {"analysis_id": analysis.id, "blueprint_id": bp.id})

@router.put("/{job_id}/blueprint")
def update_blueprint(job_id: str, payload: BlueprintUpdate, db: Session = Depends(get_db), current_company: User = Depends(require_company)):
    job = db.query(Job).filter(Job.id == job_id, Job.company_id == current_company.id).first()
    if not job:
        raise ApiError(404, "Job not found")
        
    bp = db.query(InterviewBlueprint).filter(InterviewBlueprint.job_id == job_id).first()
    if not bp:
        raise ApiError(404, "Blueprint not found")
        
    if payload.persona_level is not None:
        bp.persona_level = payload.persona_level
    if payload.estimated_duration is not None:
        bp.estimated_duration = payload.estimated_duration
    if payload.similarity_threshold is not None:
        bp.similarity_threshold = payload.similarity_threshold
    if payload.evaluation_weights is not None:
        if sum(payload.evaluation_weights.values()) != 100:
            raise ApiError(400, "Evaluation weights must total 100")
        bp.evaluation_weights = json.dumps(payload.evaluation_weights)
    if payload.question_distribution is not None:
        bp.question_distribution = json.dumps(payload.question_distribution)
        
    bp.version += 1
    db.commit()
    return ok("Blueprint updated")

@router.post("/{job_id}/publish")
def publish_job(job_id: str, db: Session = Depends(get_db), current_company: User = Depends(require_company)):
    job = db.query(Job).filter(Job.id == job_id, Job.company_id == current_company.id).first()
    if not job:
        raise ApiError(404, "Job not found")
        
    desc = db.query(JobDescription).filter(JobDescription.job_id == job_id).first()
    analysis = db.query(JdAnalysis).filter(JdAnalysis.job_id == job_id).first()
    bp = db.query(InterviewBlueprint).filter(InterviewBlueprint.job_id == job_id).first()
    
    if not all([desc, analysis, bp]):
        raise ApiError(400, "Cannot publish job without JD, Analysis, and Blueprint")
        
    job.status = JobStatus.PUBLISHED.value
    db.commit()
    return ok("Job published successfully")

"""

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)

write_file(f"{MODELS_DIR}/job.py", job_model)
write_file(f"{MODELS_DIR}/job_description.py", job_desc_model)
write_file(f"{MODELS_DIR}/jd_analysis.py", jd_analysis_model)
write_file(f"{MODELS_DIR}/interview_blueprint.py", blueprint_model)
write_file(f"{SCHEMAS_DIR}/job.py", schema_code)
write_file(f"{SERVICES_DIR}/ai_service.py", ai_service_code)
write_file(f"{ROUTES_DIR}/jobs.py", job_routes_code)

# Add to models/__init__.py
with open(f"{MODELS_DIR}/__init__.py", "a") as f:
    f.write("\nfrom app.models.job import Job\n")
    f.write("from app.models.job_description import JobDescription\n")
    f.write("from app.models.jd_analysis import JdAnalysis\n")
    f.write("from app.models.interview_blueprint import InterviewBlueprint\n")

print("Backend setup complete.")
