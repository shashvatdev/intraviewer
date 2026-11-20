"""Serialization + completion scoring for users and profiles.

Kept in one place so Module 2+ (jobs, applications) can reuse the same
public shapes without duplicating logic.
"""
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.candidate_profile import CandidateProfile
from app.models.company_profile import CompanyProfile
from app.models.user import User, UserRole


def _iso(dt) -> Optional[str]:
    return dt.isoformat() if dt else None


def get_or_create_candidate_profile(db: Session, user: User) -> CandidateProfile:
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == user.id).first()
    if profile is None:
        profile = CandidateProfile(user_id=user.id, skills=[], education=[], experience=[])
        db.add(profile)
        db.commit()
    return profile


def get_or_create_company_profile(db: Session, user: User) -> CompanyProfile:
    profile = db.query(CompanyProfile).filter(CompanyProfile.user_id == user.id).first()
    if profile is None:
        profile = CompanyProfile(user_id=user.id, company_name=user.name, business_email=user.email)
        db.add(profile)
        db.commit()
    return profile


def candidate_checklist(user: User, p: CandidateProfile) -> List[Dict[str, Any]]:
    return [
        {"key": "name", "label": "Full name", "done": bool(user.name)},
        {"key": "phone", "label": "Phone number", "done": bool(p.phone)},
        {"key": "profile_photo", "label": "Profile photo", "done": bool(p.profile_photo)},
        {"key": "skills", "label": "Skills", "done": bool(p.skills)},
        {"key": "education", "label": "Education", "done": bool(p.education)},
        {"key": "experience", "label": "Experience", "done": bool(p.experience)},
        {
            "key": "links",
            "label": "At least one link",
            "done": bool(p.github_url or p.linkedin_url or p.portfolio_url),
        },
    ]


def company_checklist(p: CompanyProfile) -> List[Dict[str, Any]]:
    return [
        {"key": "company_name", "label": "Company name", "done": bool(p.company_name)},
        {"key": "logo", "label": "Logo", "done": bool(p.logo)},
        {"key": "website", "label": "Website", "done": bool(p.website)},
        {"key": "industry", "label": "Industry", "done": bool(p.industry)},
        {"key": "description", "label": "Description", "done": bool(p.description)},
        {"key": "location", "label": "Location", "done": bool(p.location)},
    ]


def _pct(items: List[Dict[str, Any]]) -> int:
    return round(100 * sum(1 for i in items if i["done"]) / len(items)) if items else 0


def serialize_user(user: User) -> Dict[str, Any]:
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "email_verified": user.email_verified,
        "created_at": _iso(user.created_at),
    }


def serialize_candidate_profile(user: User, p: CandidateProfile) -> Dict[str, Any]:
    checklist = candidate_checklist(user, p)
    return {
        "id": p.id,
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "email_verified": user.email_verified,
        "phone": p.phone,
        "profile_photo": p.profile_photo,
        "skills": p.skills or [],
        "education": p.education or [],
        "experience": p.experience or [],
        "github_url": p.github_url,
        "linkedin_url": p.linkedin_url,
        "portfolio_url": p.portfolio_url,
        "completion": {"percentage": _pct(checklist), "items": checklist},
        "created_at": _iso(p.created_at),
        "updated_at": _iso(p.updated_at),
    }


def serialize_company_profile(user: User, p: CompanyProfile) -> Dict[str, Any]:
    checklist = company_checklist(p)
    return {
        "id": p.id,
        "user_id": user.id,
        "company_name": p.company_name,
        "business_email": p.business_email,
        "email_verified": user.email_verified,
        "logo": p.logo,
        "website": p.website,
        "industry": p.industry,
        "description": p.description,
        "location": p.location,
        "completion": {"percentage": _pct(checklist), "items": checklist},
        "created_at": _iso(p.created_at),
        "updated_at": _iso(p.updated_at),
    }


def session_payload(db: Session, user: User) -> Dict[str, Any]:
    """User + lightweight profile summary used by the app shell (nav/avatar)."""
    data = serialize_user(user)
    if user.role == UserRole.CANDIDATE.value:
        p = get_or_create_candidate_profile(db, user)
        data["avatar"] = p.profile_photo
        data["profile_completion"] = _pct(candidate_checklist(user, p))
    else:
        p = get_or_create_company_profile(db, user)
        data["avatar"] = p.logo
        data["company_name"] = p.company_name
        data["profile_completion"] = _pct(company_checklist(p))
    return data
