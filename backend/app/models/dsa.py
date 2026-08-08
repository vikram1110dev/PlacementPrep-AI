from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime, Boolean, Enum as SQLEnum, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
import uuid

from app.database.connection import Base

def generate_uuid():
    return str(uuid.uuid4())

class DifficultyLevel(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class SubmissionStatus(str, enum.Enum):
    ACCEPTED = "Accepted"
    WRONG_ANSWER = "Wrong Answer"
    TIME_LIMIT_EXCEEDED = "Time Limit Exceeded"
    MEMORY_LIMIT_EXCEEDED = "Memory Limit Exceeded"
    COMPILATION_ERROR = "Compilation Error"
    RUNTIME_ERROR = "Runtime Error"
    PENDING = "Pending"
    UNKNOWN_ERROR = "Unknown Error"

class DSAProblem(Base):
    __tablename__ = "dsa_problems"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    difficulty = Column(SQLEnum(DifficultyLevel), nullable=False)
    category = Column(String(100), nullable=False) # e.g. "Arrays", "DP"
    
    # Execution specs
    time_limit = Column(Float, default=2.0) # in seconds
    memory_limit = Column(Integer, default=256) # in MB
    
    starter_code = Column(Text, nullable=True) # JSON mapped by language if needed, or simple string
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    test_cases = relationship("DSATestCase", back_populates="problem", cascade="all, delete-orphan")
    submissions = relationship("DSASubmission", back_populates="problem", cascade="all, delete-orphan")

class DSATestCase(Base):
    __tablename__ = "dsa_test_cases"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    problem_id = Column(String(36), ForeignKey("dsa_problems.id"), nullable=False)
    
    input_data = Column(Text, nullable=False)
    expected_output = Column(Text, nullable=False)
    is_hidden = Column(Boolean, default=False)
    
    problem = relationship("DSAProblem", back_populates="test_cases")

class DSASubmission(Base):
    __tablename__ = "dsa_submissions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    problem_id = Column(String(36), ForeignKey("dsa_problems.id"), nullable=False)
    
    language = Column(String(50), nullable=False)
    code = Column(Text, nullable=False)
    status = Column(SQLEnum(SubmissionStatus), default=SubmissionStatus.PENDING)
    
    passed_tests = Column(Integer, default=0)
    total_tests = Column(Integer, default=0)
    execution_time = Column(Float, nullable=True) # in ms
    memory_usage = Column(Float, nullable=True) # in KB
    error_message = Column(Text, nullable=True)
    
    submitted_at = Column(DateTime, server_default=func.now())

    problem = relationship("DSAProblem", back_populates="submissions")

class DSAProgress(Base):
    __tablename__ = "dsa_progress"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    
    total_solved = Column(Integer, default=0)
    total_attempted = Column(Integer, default=0)
    easy_solved = Column(Integer, default=0)
    medium_solved = Column(Integer, default=0)
    hard_solved = Column(Integer, default=0)
    
    current_streak = Column(Integer, default=0)
    last_solved_date = Column(DateTime, nullable=True)
