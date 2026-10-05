import json
from sqlalchemy.orm import Session
from app.models.interview import Interview
from app.models.question import Question
from app.services.ai.groq_service import call_groq_json

def generate_questions(db: Session, interview_id: str, count: int):
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview or not interview.blueprint:
        raise Exception("Interview blueprint not found")
        
    prompt = f"""
    Generate {count} interview questions for a role with this blueprint:
    {json.dumps(interview.blueprint)}
    Do NOT generate coding tasks or LeetCode questions. Focus on: Technical conceptual, Scenario-based, Problem-solving discussion, Behavioral.
    
    Output JSON format exactly like this:
    {{
        "questions": [
            {{
                "question": "string",
                "topic": "string",
                "difficulty": "medium",
                "expected_points": ["string"],
                "time_limit": 60,
                "question_type": "Scenario-based"
            }}
        ]
    }}
    """
    
    response = call_groq_json(prompt)
    questions_data = response.get("questions", [])
    
    created_questions = []
    for q_data in questions_data:
        question = Question(
            interview_id=interview.id,
            organization_id=interview.organization_id,
            text=q_data["question"],
            time_limit_seconds=q_data.get("time_limit", 60),
            topic=q_data.get("topic"),
            difficulty=q_data.get("difficulty"),
            expected_points=q_data.get("expected_points", []),
            question_type=q_data.get("question_type"),
            is_dynamic=False
        )
        db.add(question)
        created_questions.append(question)
        
    db.commit()
    for q in created_questions:
        db.refresh(q)
    return created_questions
