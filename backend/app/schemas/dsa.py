from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class CodeExecutionRequest(BaseModel):
    language: str = Field(..., description="E.g., python, java, cpp, javascript")
    code: str = Field(..., description="Source code string")
    
class RunCodeRequest(CodeExecutionRequest):
    test_case_id: Optional[str] = None # Run specific or all sample tests

class SubmitCodeRequest(CodeExecutionRequest):
    pass

class TestCaseResponse(BaseModel):
    id: str
    input_data: str
    expected_output: str
    is_hidden: bool
    
    class Config:
        from_attributes = True

class ProblemResponse(BaseModel):
    id: str
    title: str
    slug: str
    description: str
    difficulty: str
    category: str
    time_limit: float
    memory_limit: int
    starter_code: Optional[str]
    is_active: bool
    
    # We don't expose hidden test cases, we can optionally expose samples
    test_cases: Optional[List[TestCaseResponse]] = None
    
    class Config:
        from_attributes = True

class ProblemListResponse(BaseModel):
    id: str
    title: str
    slug: str
    difficulty: str
    category: str
    status: str = "Not Attempted" # dynamically populated per user
    
    class Config:
        from_attributes = True

class ExecutionResult(BaseModel):
    status: str
    output: Optional[str] = None
    expected_output: Optional[str] = None
    execution_time: Optional[float] = None
    memory_usage: Optional[float] = None
    error_message: Optional[str] = None
    passed: bool = False

class SubmissionResultResponse(BaseModel):
    status: str
    passed_tests: int
    total_tests: int
    execution_time: Optional[float]
    memory_usage: Optional[float]
    error_message: Optional[str]
    
class DSAProgressResponse(BaseModel):
    total_solved: int
    easy_solved: int
    medium_solved: int
    hard_solved: int
    current_streak: int
    
    class Config:
        from_attributes = True

class SubmissionListResponse(BaseModel):
    id: str
    problem_id: str
    problem_title: str
    language: str
    status: str
    passed_tests: int
    total_tests: int
    submitted_at: datetime

    class Config:
        from_attributes = True

class SubmissionDetailResponse(SubmissionListResponse):
    code: str
    execution_time: Optional[float]
    memory_usage: Optional[float]
    error_message: Optional[str]

    class Config:
        from_attributes = True

class RecommendationResponse(BaseModel):
    id: str
    title: str
    difficulty: str
    category: str
    reason: str
