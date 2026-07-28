import uuid
import enum
from sqlalchemy import Column, String, Integer, ForeignKey, Text, Boolean, DateTime, Enum, Numeric, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base

def generate_uuid():
    return str(uuid.uuid4())

class DifficultyEnum(str, enum.Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"

# M:N mapping table for tags
company_question_tags = Table(
    'aptitude_company_question_tags',
    Base.metadata,
    Column('question_id', String(36), ForeignKey('aptitude_questions.id', ondelete='CASCADE'), primary_key=True),
    Column('company_id', Integer, ForeignKey('companies.id', ondelete='CASCADE'), primary_key=True)
)

class AptitudeCategory(Base):
    __tablename__ = 'aptitude_categories'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    
    topics = relationship("AptitudeTopic", back_populates="category", cascade="all, delete-orphan")

class AptitudeTopic(Base):
    __tablename__ = 'aptitude_topics'
    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey('aptitude_categories.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(100), nullable=False)
    
    category = relationship("AptitudeCategory", back_populates="topics")
    questions = relationship("AptitudeQuestion", back_populates="topic", cascade="all, delete-orphan")

class AptitudeQuestion(Base):
    __tablename__ = 'aptitude_questions'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    topic_id = Column(Integer, ForeignKey('aptitude_topics.id', ondelete='CASCADE'), nullable=False)
    question_text = Column(Text, nullable=False)
    difficulty = Column(Enum(DifficultyEnum), nullable=False)
    explanation = Column(Text)
    marks = Column(Integer, default=1)
    negative_marks = Column(Numeric(4,2), default=0.0)
    estimated_time_seconds = Column(Integer, default=60)
    
    topic = relationship("AptitudeTopic", back_populates="questions")
    options = relationship("AptitudeOption", back_populates="question", cascade="all, delete-orphan")
    
    # We will relate to Company model later, but for now we create the bridge setup.
    # companies = relationship("Company", secondary=company_question_tags)

class AptitudeOption(Base):
    __tablename__ = 'aptitude_options'
    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(String(36), ForeignKey('aptitude_questions.id', ondelete='CASCADE'), nullable=False)
    option_text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False)
    
    question = relationship("AptitudeQuestion", back_populates="options")

class PracticeSession(Base):
    __tablename__ = 'aptitude_practice_sessions'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    started_at = Column(DateTime, server_default=func.now())
    ended_at = Column(DateTime, nullable=True)
    
    attempts = relationship("QuestionAttempt", back_populates="session", cascade="all, delete-orphan")

class QuestionAttempt(Base):
    __tablename__ = 'aptitude_question_attempts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey('aptitude_practice_sessions.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    question_id = Column(String(36), ForeignKey('aptitude_questions.id', ondelete='CASCADE'), nullable=False)
    selected_option_id = Column(Integer, ForeignKey('aptitude_options.id', ondelete='SET NULL'), nullable=True)
    is_correct = Column(Boolean, nullable=False)
    time_taken_seconds = Column(Integer)
    attempted_at = Column(DateTime, server_default=func.now())
    
    session = relationship("PracticeSession", back_populates="attempts")
    question = relationship("AptitudeQuestion")
    selected_option = relationship("AptitudeOption")

class MockTest(Base):
    __tablename__ = 'mock_tests'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    duration_minutes = Column(Integer, nullable=False)
    total_marks = Column(Integer, nullable=False)
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    
    questions = relationship("MockTestQuestion", back_populates="mock_test", cascade="all, delete-orphan")
    attempts = relationship("MockTestAttempt", back_populates="mock_test", cascade="all, delete-orphan")

class MockTestQuestion(Base):
    __tablename__ = 'mock_test_questions'
    mock_test_id = Column(Integer, ForeignKey('mock_tests.id', ondelete='CASCADE'), primary_key=True)
    question_id = Column(String(36), ForeignKey('aptitude_questions.id', ondelete='CASCADE'), primary_key=True)
    order_index = Column(Integer, default=0)
    
    mock_test = relationship("MockTest", back_populates="questions")
    question = relationship("AptitudeQuestion")

class MockTestAttempt(Base):
    __tablename__ = 'mock_test_attempts'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    mock_test_id = Column(Integer, ForeignKey('mock_tests.id', ondelete='CASCADE'), nullable=False)
    score = Column(Numeric(5,2))
    started_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
    
    mock_test = relationship("MockTest", back_populates="attempts")
