import os
import json

MODELS_DIR = "app/models"
ROUTES_DIR = "app/api/routes"

# Update InterviewSession model
with open(f"{MODELS_DIR}/interview_session.py", "r") as f:
    content = f.read()

if "integrity_score = Column(Integer, default=100)" not in content:
    content = content.replace(
        "evaluation_score = Column(Integer, nullable=True)",
        "evaluation_score = Column(Integer, nullable=True)\n    integrity_score = Column(Integer, default=100)\n    proctoring_logs = Column(Text, nullable=True)"
    )
    with open(f"{MODELS_DIR}/interview_session.py", "w") as f:
        f.write(content)

# Update Interviews router
with open(f"{ROUTES_DIR}/interviews.py", "r") as f:
    routes = f.read()

new_route = """
class ProctoringEvent(BaseModel):
    event_type: str
    description: str

@router.post("/interviews/{session_id}/proctoring-event")
def log_proctoring_event(session_id: str, event: ProctoringEvent, db: Session = Depends(get_db)):
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise ApiError(404, "Session not found")
        
    logs = json.loads(session.proctoring_logs) if session.proctoring_logs else []
    
    logs.append({
        "timestamp": str(datetime.now(timezone.utc)),
        "type": event.event_type,
        "description": event.description
    })
    
    # Deduct integrity score
    deductions = {
        "TAB_SWITCH": 10,
        "MULTIPLE_FACES": 15,
        "NO_FACE": 5,
        "LOOKING_AWAY": 2,
        "COPY_PASTE": 5
    }
    
    penalty = deductions.get(event.event_type, 0)
    current_score = session.integrity_score if session.integrity_score is not None else 100
    session.integrity_score = max(0, current_score - penalty)
    
    session.proctoring_logs = json.dumps(logs)
    db.commit()
    
    return ok("Event logged", {"integrity_score": session.integrity_score})
"""

if "def log_proctoring_event" not in routes:
    routes += new_route
    with open(f"{ROUTES_DIR}/interviews.py", "w") as f:
        f.write(routes)

print("Backend proctoring updated")
