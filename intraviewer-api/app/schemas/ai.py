from pydantic import BaseModel
from typing import Optional

class AIBlueprintRequest(BaseModel):
    interview_id: str
    job_description: str
    skills: str
    difficulty: str
    duration_minutes: int

class AIGenerateQuestionsRequest(BaseModel):
    interview_id: str
    count: int = 5

class AIEvaluateAnswerRequest(BaseModel):
    answer_id: str

class AIEvaluateInterviewRequest(BaseModel):
    session_id: str
