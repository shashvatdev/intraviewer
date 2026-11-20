from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.application import Application
from app.models.interview_session import InterviewSession

db = SessionLocal()
completed_sessions = db.query(InterviewSession).filter(InterviewSession.status == "COMPLETED").all()
for s in completed_sessions:
    app = db.query(Application).filter(Application.id == s.application_id).first()
    if app and app.status == "SHORTLISTED":
        app.status = "EVALUATING"
db.commit()
print("Fixed db")
