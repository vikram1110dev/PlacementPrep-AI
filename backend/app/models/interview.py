import uuid
from sqlalchemy import Column, String, Integer, Float, ForeignKey, Text, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base

def generate_uuid():
    return str(uuid.uuid4())

class InterviewSession(Base):
    __tablename__ = 'interview_sessions'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    interview_type = Column(String(50), nullable=False) # technical, hr, behavioral, mixed, company
    role = Column(String(255), nullable=False)
    company = Column(String(255), nullable=True)
    difficulty = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, default='not_started') # not_started, in_progress, completed, abandoned
    
    start_time = Column(DateTime, server_default=func.now())
    end_time = Column(DateTime, nullable=True)
    
    # Scores
    overall_score = Column(Float, nullable=True)
    technical_score = Column(Float, nullable=True)
    communication_score = Column(Float, nullable=True)
    problem_solving_score = Column(Float, nullable=True)
    
    # Final feedback
    feedback_strengths = Column(Text, nullable=True)
    feedback_weaknesses = Column(Text, nullable=True)
    feedback_improvements = Column(Text, nullable=True)
    
    questions = relationship("InterviewQuestion", back_populates="session", cascade="all, delete-orphan", order_by="InterviewQuestion.order")

class InterviewQuestion(Base):
    __tablename__ = 'interview_questions'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey('interview_sessions.id', ondelete='CASCADE'), nullable=False)
    question_text = Column(Text, nullable=False)
    expected_answer_hints = Column(Text, nullable=True) # AI generated hints for evaluation
    order = Column(Integer, nullable=False)
    
    session = relationship("InterviewSession", back_populates="questions")
    answer = relationship("InterviewAnswer", back_populates="question", uselist=False, cascade="all, delete-orphan")

class InterviewAnswer(Base):
    __tablename__ = 'interview_answers'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    question_id = Column(String(36), ForeignKey('interview_questions.id', ondelete='CASCADE'), nullable=False, unique=True)
    user_answer = Column(Text, nullable=False)
    
    # Evaluation
    score = Column(Float, nullable=True) # out of 10 or 100
    feedback_good = Column(Text, nullable=True)
    feedback_missing = Column(Text, nullable=True)
    feedback_improve = Column(Text, nullable=True)
    model_answer = Column(Text, nullable=True) # Optional model answer
    
    created_at = Column(DateTime, server_default=func.now())
    
    question = relationship("InterviewQuestion", back_populates="answer")
