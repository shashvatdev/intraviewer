
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
            raw_text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
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

