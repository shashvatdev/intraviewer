from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import require_candidate, require_company
from app.core.database import get_db
from app.core.errors import ok
from app.models.user import User
from app.schemas.profile import CandidateProfileUpdate, CompanyProfileUpdate
from app.services.profile_service import (
    get_or_create_candidate_profile,
    get_or_create_company_profile,
    serialize_candidate_profile,
    serialize_company_profile,
)
from app.services.upload_service import delete_image, save_image

candidate_router = APIRouter(prefix="/candidate", tags=["Candidate Profile"])
company_router = APIRouter(prefix="/company", tags=["Company Profile"])


# ------------------------------- Candidate ---------------------------------
@candidate_router.get("/profile")
def get_candidate_profile(user: User = Depends(require_candidate), db: Session = Depends(get_db)):
    profile = get_or_create_candidate_profile(db, user)
    return ok("Profile loaded", serialize_candidate_profile(user, profile))


@candidate_router.put("/profile")
def update_candidate_profile(
    payload: CandidateProfileUpdate,
    user: User = Depends(require_candidate),
    db: Session = Depends(get_db),
):
    profile = get_or_create_candidate_profile(db, user)
    changes = payload.model_dump(exclude_unset=True)

    if "name" in changes and changes["name"]:
        user.name = changes.pop("name")
    else:
        changes.pop("name", None)

    for field in ("phone", "github_url", "linkedin_url", "portfolio_url"):
        if field in changes:
            setattr(profile, field, changes[field])
    if "skills" in changes:
        profile.skills = changes["skills"] or []
    if "education" in changes:
        profile.education = changes["education"] or []
    if "experience" in changes:
        profile.experience = changes["experience"] or []

    db.commit()
    return ok("Profile saved.", serialize_candidate_profile(user, profile))


@candidate_router.post("/profile/photo")
async def upload_candidate_photo(
    file: UploadFile = File(...),
    user: User = Depends(require_candidate),
    db: Session = Depends(get_db),
):
    profile = get_or_create_candidate_profile(db, user)
    path = await save_image(file, "avatars")
    old = profile.profile_photo
    profile.profile_photo = path
    db.commit()
    delete_image(old)
    return ok("Photo updated.", serialize_candidate_profile(user, profile))


@candidate_router.delete("/profile/photo")
def delete_candidate_photo(user: User = Depends(require_candidate), db: Session = Depends(get_db)):
    profile = get_or_create_candidate_profile(db, user)
    old = profile.profile_photo
    profile.profile_photo = None
    db.commit()
    delete_image(old)
    return ok("Photo removed.", serialize_candidate_profile(user, profile))


# -------------------------------- Company ----------------------------------
@company_router.get("/profile")
def get_company_profile(user: User = Depends(require_company), db: Session = Depends(get_db)):
    profile = get_or_create_company_profile(db, user)
    return ok("Company profile loaded", serialize_company_profile(user, profile))


@company_router.put("/profile")
def update_company_profile(
    payload: CompanyProfileUpdate,
    user: User = Depends(require_company),
    db: Session = Depends(get_db),
):
    profile = get_or_create_company_profile(db, user)
    changes = payload.model_dump(exclude_unset=True)

    if "company_name" in changes:
        profile.company_name = changes["company_name"]
        user.name = changes["company_name"]
    for field in ("website", "industry", "description", "location"):
        if field in changes:
            setattr(profile, field, changes[field])

    db.commit()
    return ok("Company profile saved.", serialize_company_profile(user, profile))


@company_router.post("/profile/logo")
async def upload_company_logo(
    file: UploadFile = File(...),
    user: User = Depends(require_company),
    db: Session = Depends(get_db),
):
    profile = get_or_create_company_profile(db, user)
    path = await save_image(file, "logos")
    old = profile.logo
    profile.logo = path
    db.commit()
    delete_image(old)
    return ok("Logo updated.", serialize_company_profile(user, profile))


@company_router.delete("/profile/logo")
def delete_company_logo(user: User = Depends(require_company), db: Session = Depends(get_db)):
    profile = get_or_create_company_profile(db, user)
    old = profile.logo
    profile.logo = None
    db.commit()
    delete_image(old)
    return ok("Logo removed.", serialize_company_profile(user, profile))
