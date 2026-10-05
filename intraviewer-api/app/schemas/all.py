from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class InterviewCreate(BaseModel):
    title: str
    description: Optional[str] = None

class InterviewResponse(InterviewCreate):
    id: str
    organization_id: str
    model_config = ConfigDict(from_attributes=True)

class InterviewUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class QuestionCreate(BaseModel):
    text: str
    time_limit_seconds: Optional[int] = None

class QuestionResponse(QuestionCreate):
    id: str
    interview_id: str
    organization_id: str
    model_config = ConfigDict(from_attributes=True)

class QuestionUpdate(BaseModel):
    text: Optional[str] = None
    time_limit_seconds: Optional[int] = None

class CandidateCreate(BaseModel):
    name: str
    email: str

class CandidateResponse(CandidateCreate):
    id: str
    organization_id: str
    model_config = ConfigDict(from_attributes=True)

class CandidateUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None

class SessionCreate(BaseModel):
    candidate_id: str

class SessionResponse(BaseModel):
    id: str
    interview_id: str
    candidate_id: str
    organization_id: str
    status: str
    public_token: str
    model_config = ConfigDict(from_attributes=True)

class AnswerCreate(BaseModel):
    question_id: str
    video_url: Optional[str] = None
    audio_url: Optional[str] = None
    text_answer: Optional[str] = None

class AnswerResponse(AnswerCreate):
    id: str
    session_id: str
    organization_id: str
    model_config = ConfigDict(from_attributes=True)

class EvaluationCreate(BaseModel):
    score: Optional[float] = None
    feedback: Optional[str] = None

class EvaluationResponse(EvaluationCreate):
    id: str
    session_id: str
    organization_id: str
    model_config = ConfigDict(from_attributes=True)

class AIBlueprintRequest(BaseModel):
    job_title: str
    job_description: str

class AIGenerateQuestionsRequest(BaseModel):
    blueprint: str
    count: int = 5

class AIEvaluateAnswerRequest(BaseModel):
    question: str
    answer: str

class AIEvaluateInterviewRequest(BaseModel):
    session_id: str
