import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, Text, JSON, DateTime, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base

def generate_uuid():
    return str(uuid.uuid4())

class ResumeTemplate(Base):
    __tablename__ = 'resume_templates'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False) # e.g. "Modern", "Minimal"
    html_template_path = Column(String(255))
    thumbnail_url = Column(String(255))

class UserResume(Base):
    __tablename__ = 'user_resumes'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    template_id = Column(Integer, ForeignKey('resume_templates.id', ondelete='SET NULL'), nullable=True)
    
    title = Column(String(255), nullable=False) # e.g. "Software Engineer Resume"
    is_primary = Column(Integer, default=0) # 1 if this is the default resume to show on profile
    
    # Store the entire complex structure as JSON to allow infinite flexibility for "Custom Sections"
    resume_data = Column(JSON, nullable=False)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User")
    template = relationship("ResumeTemplate")
    ats_reports = relationship("ATSReport", back_populates="resume", cascade="all, delete-orphan")

class ATSReport(Base):
    __tablename__ = 'ats_reports'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    resume_id = Column(String(36), ForeignKey('user_resumes.id', ondelete='CASCADE'), nullable=False)
    
    # Scores
    overall_score = Column(Numeric(5,2), nullable=False)
    formatting_score = Column(Numeric(5,2))
    section_completeness = Column(Numeric(5,2))
    
    # Analysis JSON blocks
    missing_skills = Column(JSON) # e.g. ["Docker", "Kubernetes"]
    keyword_matches = Column(JSON)
    industry_suggestions = Column(JSON)
    
    generated_at = Column(DateTime, server_default=func.now())

    resume = relationship("UserResume", back_populates="ats_reports")
