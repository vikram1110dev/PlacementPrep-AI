from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ConversationCreate(BaseModel):
    title: str = "New Conversation"
    mode: str = "general"

class ConversationUpdate(BaseModel):
    title: str

class ConversationResponse(BaseModel):
    id: str
    title: str
    mode: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    message: str
    conversation_id: str
    stream: bool = True

class ChatResponse(BaseModel):
    conversation_id: str
    message: str
    
    class Config:
        from_attributes = True

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
