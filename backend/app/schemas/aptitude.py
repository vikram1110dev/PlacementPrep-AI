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



class QuestionCreate(BaseModel):
    topic_id: int
    question_text: str
    difficulty: DifficultyEnum
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str
    explanation: Optional[str] = None
    marks: int = 1
    negative_marks: Decimal = 0.0
    estimated_time_seconds: int = 60
    company: Optional[str] = None
    tags: Optional[str] = None

class QuestionResponse(BaseModel):
    id: str
    topic_id: int
    question_text: str
    difficulty: DifficultyEnum
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str
    explanation: Optional[str] = None
    marks: int
    negative_marks: Decimal
    estimated_time_seconds: int
    is_active: bool
    company: Optional[str] = None
    tags: Optional[str] = None
    created_by: Optional[str] = None
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    class Config: from_attributes = True

class QuestionFilter(BaseModel):
    topic_id: Optional[int] = None
    difficulty: Optional[DifficultyEnum] = None
    company: Optional[str] = None
    tags: Optional[str] = None
    is_active: Optional[bool] = None
    search: Optional[str] = None
    include_deleted: bool = False
    skip: int = 0
    limit: int = 20

# --- Practice Sessions ---
class SubmitAnswerRequest(BaseModel):
    question_id: str
    selected_answer: Optional[str] = None # None means skipped
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

# --- Test Engine ---
class TestSetupRequest(BaseModel):
    topic_id: Optional[int] = None
    difficulty: Optional[DifficultyEnum] = None
    question_count: int = 10

class TestQuestionResponse(BaseModel):
    id: str
    question_text: str
    options: List[str] # Array of options, randomized by backend
    time_limit_seconds: int

class TestSessionResponse(BaseModel):
    session_id: str
    started_at: datetime
    questions: List[TestQuestionResponse]

class AnswerSubmitRequest(BaseModel):
    question_id: str
    selected_answer: Optional[str] = None
    time_taken_seconds: int
    visited: bool = True
    marked_for_review: bool = False

class TestResultResponse(BaseModel):
    session_id: str
    score: Decimal
    accuracy_percentage: Decimal
    total_questions: int
    correct_answers: int
    wrong_answers: int
    skipped_answers: int
    time_taken_seconds: int
    
class TestHistoryResponse(BaseModel):
    session_id: str
    started_at: datetime
    status: str
    score: Decimal
    accuracy_percentage: Decimal
    total_questions: int

# --- Analytics ---
class WeakTopicAnalysis(BaseModel):
    topic_name: str
    accuracy_percentage: Decimal
    total_attempts: int

class HistoryResponse(BaseModel):
    session_id: str
    started_at: datetime
    ended_at: Optional[datetime]
    total_questions: int
    correct_answers: int
    score: Decimal
    accuracy_percentage: Decimal

class ProgressResponse(BaseModel):
    total_tests_taken: int
    overall_accuracy: Decimal
    average_score: Decimal
    strongest_topic: Optional[str]
    weakest_topic: Optional[str]
    time_spent_minutes: int
