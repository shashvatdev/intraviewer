import json
from sqlalchemy.orm import Session
from app.models.answer import Answer
from app.models.question import Question
from app.models.interview_session import InterviewSession
from app.models.evaluation import Evaluation
from app.services.ai.groq_service import call_groq_json

def evaluate_and_next_question(db: Session, answer_id: str):
    answer = db.query(Answer).filter(Answer.id == answer_id).first()
    if not answer:
        raise Exception("Answer not found")
        
    question = db.query(Question).filter(Question.id == answer.question_id).first()
    
    prompt = f"""
    You are an expert technical interviewer.
    The question was: "{question.text}"
    The candidate answered: "{answer.text_answer}"
    Expected points: {json.dumps(question.expected_points)}
    
    Please evaluate the answer and generate a follow-up question. 
    Output JSON format exactly like this:
    {{
        "score": 8.5,
        "strengths": ["string"],
        "weaknesses": ["string"],
        "feedback": "string",
        "next_question": {{
            "question": "string",
            "topic": "string",
            "difficulty": "hard",
            "expected_points": ["string"],
            "time_limit": 60,
            "question_type": "Follow-up"
        }}
    }}
    """
    
    response = call_groq_json(prompt)
    
    answer.ai_score = response.get("score")
    answer.ai_strengths = response.get("strengths", [])
    answer.ai_weaknesses = response.get("weaknesses", [])
    answer.ai_feedback = response.get("feedback", "")
    db.commit()
    
    next_q_data = response.get("next_question")
    next_q = None
    if next_q_data:
        next_q = Question(
            interview_id=question.interview_id,
            organization_id=question.organization_id,
            session_id=answer.session_id,
            text=next_q_data["question"],
            time_limit_seconds=next_q_data.get("time_limit", 60),
            topic=next_q_data.get("topic"),
            difficulty=next_q_data.get("difficulty"),
            expected_points=next_q_data.get("expected_points", []),
            question_type=next_q_data.get("question_type"),
            is_dynamic=True
        )
        db.add(next_q)
        db.commit()
        db.refresh(next_q)
        
    return {
        "evaluation": {
            "score": answer.ai_score,
            "strengths": answer.ai_strengths,
            "weaknesses": answer.ai_weaknesses,
            "feedback": answer.ai_feedback
        },
        "next_question": next_q
    }

def evaluate_interview(db: Session, session_id: str):
    answers = db.query(Answer).filter(Answer.session_id == session_id).all()
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise Exception("Session not found")
        
    history = []
    for ans in answers:
        q = db.query(Question).filter(Question.id == ans.question_id).first()
        history.append({
            "question": q.text,
            "answer": ans.text_answer,
            "score": ans.ai_score
        })
        
    prompt = f"""
    Evaluate the full interview session based on these Q&A:
    {json.dumps(history)}
    
    Output JSON format exactly like this:
    {{
        "overall_score": 8.0,
        "final_report": "string",
        "recommendation": "Strong Hire"
    }}
    """
    response = call_groq_json(prompt)
    
    evaluation = db.query(Evaluation).filter(Evaluation.session_id == session_id).first()
    if not evaluation:
        evaluation = Evaluation(session_id=session_id, organization_id=session.organization_id)
        db.add(evaluation)
    
    evaluation.overall_score = response.get("overall_score")
    evaluation.final_report = response.get("final_report")
    evaluation.recommendation = response.get("recommendation")
    db.commit()
    db.refresh(evaluation)
    
    return evaluation
