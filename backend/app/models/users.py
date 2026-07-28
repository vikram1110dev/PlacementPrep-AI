from sqlalchemy import Column, String, Integer, ForeignKey, Text, Date, Numeric, Enum, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base
import enum

class GenderEnum(str, enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"
    PREFER_NOT_TO_SAY = "PREFER_NOT_TO_SAY"

class SkillCategoryEnum(str, enum.Enum):
    TECHNICAL = "TECHNICAL"
    SOFT = "SOFT"
    TOOL = "TOOL"

class SkillProficiencyEnum(str, enum.Enum):
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"

class StudentProfile(Base):
    __tablename__ = 'student_profiles'
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    phone_number = Column(String(20))
    dob = Column(Date)
    gender = Column(Enum(GenderEnum))
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100))
    bio = Column(Text)
    profile_photo_url = Column(String(255))
    college = Column(String(255))
    university = Column(String(255))
    department = Column(String(100))
    degree = Column(String(100))
    current_year = Column(Integer)
    graduation_year = Column(Integer)
    cgpa = Column(Numeric(4,2))
    
    # Gamification / Stats
    placement_score = Column(Integer, default=0)
    current_xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    streak_days = Column(Integer, default=0)
    
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="student_profile")

class Education(Base):
    __tablename__ = 'education'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    institution = Column(String(255), nullable=False)
    degree = Column(String(100), nullable=False)
    department = Column(String(100))
    start_year = Column(Integer)
    end_year = Column(Integer)
    cgpa = Column(Numeric(4,2))
    
    user = relationship("User", back_populates="education_history")

class Skill(Base):
    __tablename__ = 'skills'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    category = Column(Enum(SkillCategoryEnum), nullable=False)
    
    # M:N relationship handled by StudentSkill

class StudentSkill(Base):
    __tablename__ = 'student_skills'
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    skill_id = Column(Integer, ForeignKey('skills.id', ondelete='CASCADE'), primary_key=True)
    proficiency = Column(Enum(SkillProficiencyEnum), default=SkillProficiencyEnum.BEGINNER)
    
    user = relationship("User", back_populates="skills")
    skill = relationship("Skill")

class Certificate(Base):
    __tablename__ = 'certificates'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = Column(String(255), nullable=False)
    provider = Column(String(100), nullable=False)
    issue_date = Column(Date)
    credential_url = Column(String(255))
    certificate_file_url = Column(String(255))
    
    user = relationship("User", back_populates="certificates")

class Achievement(Base):
    __tablename__ = 'achievements'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    date_achieved = Column(Date)
    badge_url = Column(String(255))
    
    user = relationship("User", back_populates="achievements")

class SocialLink(Base):
    __tablename__ = 'social_links'
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    github_url = Column(String(255))
    linkedin_url = Column(String(255))
    portfolio_url = Column(String(255))
    leetcode_url = Column(String(255))
    hackerrank_url = Column(String(255))
    codechef_url = Column(String(255))
    codeforces_url = Column(String(255))
    
    user = relationship("User", back_populates="social_links")

class LearningPreference(Base):
    __tablename__ = 'student_preferences' # Aligning with earlier schema naming, or 'learning_preferences'
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    preferred_programming_language = Column(String(50))
    study_hours_per_day = Column(Integer, default=2)
    target_company = Column(String(100))
    email_notifications = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=True)
    theme = Column(String(20), default="SYSTEM")
    
    user = relationship("User", back_populates="learning_preferences")
