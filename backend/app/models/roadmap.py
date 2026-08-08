import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base

def generate_uuid():
    return str(uuid.uuid4())

class Roadmap(Base):
    __tablename__ = 'roadmaps'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    target_role = Column(String(255), nullable=False)
    target_company = Column(String(255), nullable=True)
    duration_weeks = Column(Integer, nullable=False, default=4)
    daily_time_minutes = Column(Integer, nullable=False, default=60)
    ai_recommendation_summary = Column(Text, nullable=True)
    version = Column(Integer, nullable=False, default=1)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, server_default=func.now())
    
    weeks = relationship("RoadmapWeek", back_populates="roadmap", cascade="all, delete-orphan", order_by="RoadmapWeek.week_number")

class RoadmapWeek(Base):
    __tablename__ = 'roadmap_weeks'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    roadmap_id = Column(String(36), ForeignKey('roadmaps.id', ondelete='CASCADE'), nullable=False)
    week_number = Column(Integer, nullable=False)
    focus_area = Column(String(255), nullable=True)
    
    roadmap = relationship("Roadmap", back_populates="weeks")
    tasks = relationship("RoadmapTask", back_populates="week", cascade="all, delete-orphan", order_by="RoadmapTask.day_number")

class RoadmapTask(Base):
    __tablename__ = 'roadmap_tasks'
    id = Column(String(36), primary_key=True, default=generate_uuid)
    week_id = Column(String(36), ForeignKey('roadmap_weeks.id', ondelete='CASCADE'), nullable=False)
    day_number = Column(Integer, nullable=False) # 1 to 7
    topic = Column(String(255), nullable=False)
    activity = Column(Text, nullable=False)
    estimated_time = Column(Integer, nullable=False) # in minutes
    difficulty = Column(String(50), nullable=True)
    expected_outcome = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default='not_started') # not_started, in_progress, completed, skipped
    
    week = relationship("RoadmapWeek", back_populates="tasks")
