
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class JobCreate(BaseModel):
    title: str
    department: Optional[str] = None
    ctc_type: Optional[str] = None
    ctc_min: Optional[str] = None
    ctc_max: Optional[str] = None
    currency: Optional[str] = "INR"
    work_start_time: Optional[str] = None
    work_end_time: Optional[str] = None
    timezone: Optional[str] = None
    shift_type: Optional[str] = None
    work_mode: Optional[str] = None
    location: Optional[str] = None
    relocation_required: Optional[bool] = False
    deadline: Optional[datetime] = None

class JobUpdate(BaseModel):
    title: Optional[str] = None
    department: Optional[str] = None
    ctc_type: Optional[str] = None
    ctc_min: Optional[str] = None
    ctc_max: Optional[str] = None
    currency: Optional[str] = None
    work_start_time: Optional[str] = None
    work_end_time: Optional[str] = None
    timezone: Optional[str] = None
    shift_type: Optional[str] = None
    work_mode: Optional[str] = None
    location: Optional[str] = None
    relocation_required: Optional[bool] = None
    deadline: Optional[datetime] = None

class ManualJdUpload(BaseModel):
    raw_text: str

class BlueprintUpdate(BaseModel):
    persona_level: Optional[str] = None
    estimated_duration: Optional[int] = None
    question_distribution: Optional[Dict[str, Any]] = None
    evaluation_weights: Optional[Dict[str, int]] = None
    similarity_threshold: Optional[int] = None
