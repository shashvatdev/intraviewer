import os

ROUTES_DIR = "app/api/routes"

with open(f"{ROUTES_DIR}/applications.py", "r") as f:
    content = f.read()

# Make the company applications endpoint also return the interview session data
old_query = """    apps = db.query(Application, User).join(User, Application.candidate_id == User.id).filter(Application.job_id == job_id).order_by(desc(Application.match_score)).all()
    
    res = []
    for app, candidate in apps:
        analysis = json.loads(app.match_analysis) if app.match_analysis else {}
        res.append({"""

new_query = """    from app.models.interview_session import InterviewSession
    apps = db.query(Application, User).join(User, Application.candidate_id == User.id).filter(Application.job_id == job_id).order_by(desc(Application.match_score)).all()
    
    res = []
    for app, candidate in apps:
        session = db.query(InterviewSession).filter(InterviewSession.application_id == app.id).first()
        session_data = None
        if session:
            session_data = {
                "status": session.status,
                "evaluation_score": session.evaluation_score,
                "integrity_score": session.integrity_score,
                "proctoring_logs": json.loads(session.proctoring_logs) if session.proctoring_logs else [],
                "transcript": json.loads(session.transcript) if session.transcript else []
            }
            
        analysis = json.loads(app.match_analysis) if app.match_analysis else {}
        res.append({
            "session": session_data,"""

content = content.replace(old_query, new_query)

with open(f"{ROUTES_DIR}/applications.py", "w") as f:
    f.write(content)

print("Updated company applications endpoint with interview report data")
