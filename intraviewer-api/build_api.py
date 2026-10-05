import os

# Create security dependency
os.makedirs("app/core", exist_ok=True)
with open("app/core/security.py", "w") as f:
    f.write("""from fastapi import Security, HTTPException, status, Depends
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.api_key import APIKey
from app.models.organization import Organization

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

def get_current_organization(
    key: str = Security(api_key_header),
    db: Session = Depends(get_db)
) -> Organization:
    api_key = db.query(APIKey).filter(APIKey.key == key, APIKey.is_active == True).first()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API Key"
        )
    organization = db.query(Organization).filter(Organization.id == api_key.organization_id).first()
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Organization not found"
        )
    return organization
""")

# Models
os.makedirs("app/models", exist_ok=True)

with open("app/models/interview.py", "w") as f:
    f.write("""from uuid import uuid4
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Interview(Base):
    __tablename__ = "interviews"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=True)
""")

with open("app/models/question.py", "w") as f:
    f.write("""from uuid import uuid4
from sqlalchemy import String, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Question(Base):
    __tablename__ = "questions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    interview_id: Mapped[str] = mapped_column(String(36), ForeignKey("interviews.id"), nullable=False)
    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id"), nullable=False)
    text: Mapped[str] = mapped_column(String(1000), nullable=False)
    time_limit_seconds: Mapped[int] = mapped_column(Integer, nullable=True)
""")

with open("app/models/candidate.py", "w") as f:
    f.write("""from uuid import uuid4
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Candidate(Base):
    __tablename__ = "candidates"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
""")

with open("app/models/interview_session.py", "w") as f:
    f.write("""from uuid import uuid4
import secrets
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class InterviewSession(Base):
    __tablename__ = "interview_sessions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    interview_id: Mapped[str] = mapped_column(String(36), ForeignKey("interviews.id"), nullable=False)
    candidate_id: Mapped[str] = mapped_column(String(36), ForeignKey("candidates.id"), nullable=False)
    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    public_token: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, default=lambda: secrets.token_urlsafe(32))
""")

with open("app/models/answer.py", "w") as f:
    f.write("""from uuid import uuid4
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Answer(Base):
    __tablename__ = "answers"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("interview_sessions.id"), nullable=False)
    question_id: Mapped[str] = mapped_column(String(36), ForeignKey("questions.id"), nullable=False)
    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id"), nullable=False)
    video_url: Mapped[str] = mapped_column(String(1000), nullable=True)
    audio_url: Mapped[str] = mapped_column(String(1000), nullable=True)
    text_answer: Mapped[str] = mapped_column(String(2000), nullable=True)
""")

with open("app/models/evaluation.py", "w") as f:
    f.write("""from uuid import uuid4
from sqlalchemy import String, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Evaluation(Base):
    __tablename__ = "evaluations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("interview_sessions.id"), nullable=False)
    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id"), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=True)
    feedback: Mapped[str] = mapped_column(String(2000), nullable=True)
""")

with open("app/models/__init__.py", "w") as f:
    f.write("""from app.models.organization import Organization
from app.models.api_key import APIKey
from app.models.interview import Interview
from app.models.question import Question
from app.models.candidate import Candidate
from app.models.interview_session import InterviewSession
from app.models.answer import Answer
from app.models.evaluation import Evaluation
""")

