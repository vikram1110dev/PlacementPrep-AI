from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from app.models.aptitude import DifficultyEnum

# --- Category & Topic ---
class CategoryBase(BaseModel):
    name: str

class CategoryResponse(CategoryBase):
    id: int
    class Config: from_attributes = True

class TopicBase(BaseModel):
    category_id: int
    name: str

class TopicResponse(TopicBase):
    id: int
    category: CategoryResponse
    class Config: from_attributes = True

# --- Options & Questions ---
class OptionBase(BaseModel):
    option_text: str
    is_correct: bool = False

class OptionResponse(OptionBase):
    id: int
    class Config: from_attributes = True

class QuestionCreate(BaseModel):
    topic_id: int
    question_text: str
    difficulty: DifficultyEnum
    explanation: Optional[str] = None
    marks: int = 1
    negative_marks: Decimal = 0.0
    estimated_time_seconds: int = 60
    options: List[OptionBase] = Field(..., min_items=2, max_items=5)

class QuestionResponse(BaseModel):
    id: str
    topic_id: int
    question_text: str
    difficulty: DifficultyEnum
    explanation: Optional[str] = None
    marks: int
    negative_marks: Decimal
    estimated_time_seconds: int
    options: List[OptionResponse]
    class Config: from_attributes = True

class QuestionFilter(BaseModel):
    topic_id: Optional[int] = None
    difficulty: Optional[DifficultyEnum] = None
    skip: int = 0
    limit: int = 20

# --- Practice Sessions ---
class SubmitAnswerRequest(BaseModel):
    question_id: str
    selected_option_id: Optional[int] = None # None means skipped
    time_taken_seconds: int

class PracticeSessionResponse(BaseModel):
    session_id: str
    started_at: datetime

# --- Mock Tests ---
class MockTestCreate(BaseModel):
    title: str
    description: Optional[str] = None
    duration_minutes: int
    total_marks: int
    question_ids: List[str]

class MockTestResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    duration_minutes: int
    total_marks: int
    is_published: bool
    class Config: from_attributes = True

class MockTestSubmission(BaseModel):
    answers: List[SubmitAnswerRequest]

class MockTestResult(BaseModel):
    score: Decimal
    total_marks: int
    correct_answers: int
    wrong_answers: int
    skipped_answers: int
    accuracy_percentage: Decimal

# --- Analytics ---
class WeakTopicAnalysis(BaseModel):
    topic_name: str
    accuracy_percentage: Decimal
    total_attempts: int
