import sys
import os
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User
from app.models.candidate_profile import CandidateProfile
from app.models.company_profile import CompanyProfile

def seed():
    db = SessionLocal()
    
    # Candidate
    candidate_email = "candidate@example.com"
    candidate = db.query(User).filter(User.email == candidate_email).first()
    if not candidate:
        candidate = User(
            name="John Candidate",
            email=candidate_email,
            password_hash=hash_password("Password123"),
            role="CANDIDATE",
            email_verified=True
        )
        db.add(candidate)
        db.flush()
        profile = CandidateProfile(
            user_id=candidate.id,
            phone="1234567890",
            skills="[\"Python\", \"React\"]"
        )
        db.add(profile)
        print(f"Created candidate: {candidate_email} / Password123")
    else:
        print(f"Candidate already exists: {candidate_email} / Password123")

    # Company
    company_email = "hr@acmecorp.com"
    company = db.query(User).filter(User.email == company_email).first()
    if not company:
        company = User(
            name="Acme Corp HR",
            email=company_email,
            password_hash=hash_password("Password123"),
            role="COMPANY",
            email_verified=True
        )
        db.add(company)
        db.flush()
        c_profile = CompanyProfile(
            user_id=company.id,
            company_name="Acme Corp",
            business_email=company_email,
            industry="Software"
        )
        db.add(c_profile)
        print(f"Created company: {company_email} / Password123")
    else:
        print(f"Company already exists: {company_email} / Password123")

    db.commit()
    db.close()

if __name__ == "__main__":
    seed()
