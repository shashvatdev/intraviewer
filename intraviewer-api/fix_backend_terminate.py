import os

ROUTES_DIR = "app/api/routes"

with open(f"{ROUTES_DIR}/interviews.py", "r") as f:
    content = f.read()

new_endpoint = """
@router.post("/interviews/{session_id}/terminate")
def terminate_interview(session_id: str, db: Session = Depends(get_db)):
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise ApiError(404, "Session not found")
        
    session.status = "COMPLETED"
    session.completed_at = datetime.now(timezone.utc)
    
    app = db.query(Application).filter(Application.id == session.application_id).first()
    if app:
        app.status = "EVALUATING"
        
    db.commit()
    return ok("Terminated successfully")
"""

if "def terminate_interview" not in content:
    content += new_endpoint
    with open(f"{ROUTES_DIR}/interviews.py", "w") as f:
        f.write(content)

print("Added terminate endpoint to backend")
