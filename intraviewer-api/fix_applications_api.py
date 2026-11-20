import os

ROUTES_DIR = "app/api/routes"

with open(f"{ROUTES_DIR}/applications.py", "r") as f:
    content = f.read()

old_res = """                "evaluation_score": session.evaluation_score,
                "integrity_score": session.integrity_score,
                "proctoring_logs": json.loads(session.proctoring_logs) if session.proctoring_logs else [],
                "transcript": json.loads(session.transcript) if session.transcript else []"""

new_res = """                "evaluation_score": session.evaluation_score,
                "integrity_score": session.integrity_score,
                "proctoring_logs": json.loads(session.proctoring_logs) if session.proctoring_logs else [],
                "transcript": json.loads(session.transcript) if session.transcript else [],
                "evaluation_details": json.loads(session.evaluation_details) if session.evaluation_details else {}"""

content = content.replace(old_res, new_res)

with open(f"{ROUTES_DIR}/applications.py", "w") as f:
    f.write(content)

print("Updated applications to send eval details")
