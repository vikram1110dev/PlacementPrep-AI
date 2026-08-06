from sqlalchemy import Column, String, Integer, ForeignKey, Text, JSON, DateTime, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base
from app.models.admin import Company

class CompanyPattern(Base):
    __tablename__ = 'company_patterns'
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    role_name = Column(String(255), nullable=False) # e.g. "SDE 1", "Ninja"
    duration_minutes = Column(Integer, nullable=False, default=90)
    total_questions = Column(Integer, nullable=False, default=50)
    sections = Column(JSON, nullable=False) # e.g. [{"name": "Quants", "questions": 20}, {"name": "Logical", "questions": 15}]
    difficulty_distribution = Column(JSON, nullable=True) # e.g. {"EASY": 10, "MEDIUM": 20, "HARD": 20}
    created_at = Column(DateTime, server_default=func.now())

    company = relationship("Company")

class CompanyPreviousYearStats(Base):
    __tablename__ = 'company_stats'
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey('companies.id', ondelete='CASCADE'), nullable=False, unique=True)
    avg_package = Column(String(100)) # e.g. "15L - 40L"
    competition_level = Column(String(50)) # e.g. "High", "Medium", "Low"
    success_rate_percent = Column(Numeric(5,2)) # e.g. 3.5
    hiring_mode = Column(String(100)) # e.g. "Off-Campus, On-Campus"
    created_at = Column(DateTime, server_default=func.now())
    
    company = relationship("Company")
