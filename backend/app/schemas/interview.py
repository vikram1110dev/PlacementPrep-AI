from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class InterviewSetupRequest(BaseModel):
    interview_type: str = Field(..., description="e.g., technical, hr, behavioral, company")
    role: str = Field(..., description="e.g., Software Developer")
    company: Optional[str] = Field(None, description="e.g., Google, Amazon")
    difficulty: str = Field(..., description="e.g., easy, medium, hard")
    num_questions: int = Field(5, ge=1, le=15)

class InterviewQuestionResponse(BaseModel):
    id: str
    order: int
    question_text: str

class InterviewAnswerRequest(BaseModel):
    answer_text: str

class InterviewEvaluationResponse(BaseModel):
    score: float
    feedback_good: str
    feedback_missing: str
    feedback_improve: str
    model_answer: Optional[str] = None

class InterviewSessionStateResponse(BaseModel):
    session_id: str
    status: str
    current_question: Optional[InterviewQuestionResponse] = None
    total_questions: int
    questions_answered: int
    is_complete: bool

class InterviewReportResponse(BaseModel):
    session_id: str
    interview_type: str
    role: str
    company: Optional[str]
    difficulty: str
    overall_score: Optional[float]
    technical_score: Optional[float]
    communication_score: Optional[float]
    problem_solving_score: Optional[float]
    feedback_strengths: Optional[str]
    feedback_weaknesses: Optional[str]
    feedback_improvements: Optional[str]
    completed_at: Optional[datetime]
