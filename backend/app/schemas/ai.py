from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

class ChatMessage(BaseModel):
    role: str = Field(..., description="Role of the sender: user, assistant, system")
    content: str

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    stream: bool = True

class ChatResponse(BaseModel):
    session_id: str
    message: str

class AgentAction(BaseModel):
    agent: str
    action: str
    input: str

class StudyPlanRequest(BaseModel):
    target_role: str
    duration_weeks: int
    current_level: str

class ResumeReviewRequest(BaseModel):
    resume_text: str
    job_description: Optional[str] = None

class MockInterviewRequest(BaseModel):
    topic: str
    difficulty: str

class AIAnalyticsResponse(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_estimate: float
    total_sessions: int
