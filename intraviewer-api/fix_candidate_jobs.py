import os

ROUTES_DIR = "app/api/routes"

candidate_jobs_code = """
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc, asc
from typing import Optional, List
from datetime import datetime, timezone
from app.core.database import get_db
from app.api.deps import require_candidate
from app.models.user import User
from app.models.company_profile import CompanyProfile
from app.models.job import Job, JobStatus
from app.models.jd_analysis import JdAnalysis
from app.models.application import Application
from app.core.errors import ok, ApiError
import json
import math

router = APIRouter(prefix="/candidate/jobs", tags=["Candidate Jobs"])

def utc_now():
    return datetime.now(timezone.utc)

@router.get("/search")
def search_jobs(
    q: Optional[str] = None,
    location: Optional[str] = None,
    experience_min: Optional[int] = None,
    experience_max: Optional[int] = None,
    ctc_min: Optional[int] = None,
    work_mode: Optional[str] = None,
    sort: Optional[str] = "newest",
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_candidate)
):
    now = utc_now()
    
    query = db.query(Job, CompanyProfile, JdAnalysis).join(
        CompanyProfile, Job.company_id == CompanyProfile.user_id
    ).outerjoin(
        JdAnalysis, Job.id == JdAnalysis.job_id
    ).filter(
        Job.status == JobStatus.PUBLISHED.value,
        or_(Job.deadline.is_(None), Job.deadline >= now)
    )
    
    if q:
        search_term = f"%{q.lower()}%"
        query = query.filter(
            or_(
                Job.title.ilike(search_term),
                Job.department.ilike(search_term),
                CompanyProfile.company_name.ilike(search_term),
                JdAnalysis.required_skills.ilike(search_term)
            )
        )
        
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
        
    if work_mode:
        query = query.filter(Job.work_mode.ilike(work_mode))
        
    if experience_min is not None:
        query = query.filter(JdAnalysis.maximum_experience >= experience_min)
        
    if experience_max is not None:
        query = query.filter(JdAnalysis.minimum_experience <= experience_max)
        
    if sort == "newest":
        query = query.order_by(desc(Job.created_at))
    elif sort == "deadline_soon":
        query = query.order_by(asc(Job.deadline))
    
    total = query.count()
    total_pages = math.ceil(total / limit)
    
    jobs_data = query.offset((page - 1) * limit).limit(limit).all()
    
    # Get all applications for this user
    applied_job_ids = {app.job_id for app in db.query(Application).filter(Application.candidate_id == current_user.id).all()}
    
    result = []
    for job, company, analysis in jobs_data:
        skills = []
        if analysis and analysis.required_skills:
            try:
                skills = json.loads(analysis.required_skills)
            except:
                pass
                
        result.append({
            "id": job.id,
            "title": job.title,
            "company_name": company.company_name or "Confidential",
            "location": job.location,
            "work_mode": job.work_mode,
            "ctc_min": job.ctc_min,
            "ctc_max": job.ctc_max,
            "experience_min": analysis.minimum_experience if analysis else None,
            "experience_max": analysis.maximum_experience if analysis else None,
            "required_skills": skills,
            "created_at": str(job.created_at),
            "deadline": str(job.deadline) if job.deadline else None,
            "has_applied": job.id in applied_job_ids
        })
        
    return ok("Jobs fetched", {
        "jobs": result,
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages
    })

@router.get("/recommended")
def recommended_jobs(
    limit: int = Query(3, ge=1, le=10),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_candidate)
):
    now = utc_now()
    query = db.query(Job, CompanyProfile, JdAnalysis).join(
        CompanyProfile, Job.company_id == CompanyProfile.user_id
    ).outerjoin(
        JdAnalysis, Job.id == JdAnalysis.job_id
    ).filter(
        Job.status == JobStatus.PUBLISHED.value,
        or_(Job.deadline.is_(None), Job.deadline >= now)
    ).order_by(desc(Job.created_at)).limit(limit)
    
    applied_job_ids = {app.job_id for app in db.query(Application).filter(Application.candidate_id == current_user.id).all()}
    
    result = []
    for job, company, analysis in query.all():
        skills = []
        if analysis and analysis.required_skills:
            try:
                skills = json.loads(analysis.required_skills)
            except:
                pass
                
        result.append({
            "id": job.id,
            "title": job.title,
            "company_name": company.company_name or "Confidential",
            "location": job.location,
            "work_mode": job.work_mode,
            "ctc_min": job.ctc_min,
            "ctc_max": job.ctc_max,
            "experience_min": analysis.minimum_experience if analysis else None,
            "experience_max": analysis.maximum_experience if analysis else None,
            "required_skills": skills,
            "created_at": str(job.created_at),
            "deadline": str(job.deadline) if job.deadline else None,
            "has_applied": job.id in applied_job_ids
        })
        
    return ok("Recommended jobs", {"jobs": result})
"""

with open(f"{ROUTES_DIR}/candidate_jobs.py", "w") as f:
    f.write(candidate_jobs_code)

print("Fixed candidate_jobs.py")
