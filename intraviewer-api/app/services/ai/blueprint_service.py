import json
from sqlalchemy.orm import Session
from app.models.interview import Interview
from app.services.ai.groq_service import call_groq_json

def generate_blueprint(db: Session, interview_id: str, job_description: str, skills: str, difficulty: str, duration: int):
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise Exception("Interview not found")

    prompt = f"""
    Create an interview blueprint based on the following:
    Job Description: {job_description}
    Skills: {skills}
    Difficulty: {difficulty}
    Duration (minutes): {duration}
    
    Output JSON format exactly like this:
    {{
        "topics": ["string"],
        "number_of_questions": 5,
        "difficulty_distribution": {{"easy": 1, "medium": 3, "hard": 1}},
        "question_types": ["Technical conceptual", "Scenario-based"],
        "evaluation_criteria": ["string"],
        "time_allocation": {{"Technical": "30 mins"}}
    }}
    """
    
    blueprint_json = call_groq_json(prompt)
    interview.job_description = job_description
    interview.skills = skills
    interview.difficulty = difficulty
    interview.duration_minutes = duration
    interview.blueprint = blueprint_json
    db.commit()
    db.refresh(interview)
    
    return blueprint_json
