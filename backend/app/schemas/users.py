from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from datetime import date
from decimal import Decimal
from app.models.users import GenderEnum, SkillCategoryEnum, SkillProficiencyEnum

# ----------------- Student Profile -----------------
class StudentProfileBase(BaseModel):
    phone_number: Optional[str] = Field(None, pattern=r"^\+?[1-9]\d{1,14}$")
    dob: Optional[date] = None
    gender: Optional[GenderEnum] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    bio: Optional[str] = None
    college: Optional[str] = None
    university: Optional[str] = None
    department: Optional[str] = None
    degree: Optional[str] = None
    current_year: Optional[int] = Field(None, ge=1, le=5)
    graduation_year: Optional[int] = Field(None, ge=1990)
    cgpa: Optional[Decimal] = Field(None, ge=0.0, le=10.0)

class StudentProfileCreate(StudentProfileBase):
    pass

class StudentProfileResponse(StudentProfileBase):
    profile_photo_url: Optional[str] = None
    placement_score: int
    current_xp: int
    level: int
    streak_days: int

    class Config:
        from_attributes = True

# ----------------- Education -----------------
class EducationBase(BaseModel):
    institution: str = Field(..., min_length=2)
    degree: str
    department: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    cgpa: Optional[Decimal] = Field(None, ge=0.0, le=10.0)

class EducationCreate(EducationBase):
    pass

class EducationResponse(EducationBase):
    id: int
    
    class Config:
        from_attributes = True

# ----------------- Skills -----------------
class SkillResponse(BaseModel):
    id: int
    name: str
    category: SkillCategoryEnum
    
    class Config:
        from_attributes = True

class StudentSkillAdd(BaseModel):
    skill_id: int
    proficiency: SkillProficiencyEnum = SkillProficiencyEnum.BEGINNER

class StudentSkillResponse(BaseModel):
    skill: SkillResponse
    proficiency: SkillProficiencyEnum
    
    class Config:
        from_attributes = True

# ----------------- Certificates -----------------
class CertificateBase(BaseModel):
    title: str = Field(..., min_length=2)
    provider: str
    issue_date: Optional[date] = None
    credential_url: Optional[str] = None

class CertificateCreate(CertificateBase):
    pass

class CertificateResponse(CertificateBase):
    id: int
    certificate_file_url: Optional[str] = None
    
    class Config:
        from_attributes = True

# ----------------- Achievements -----------------
class AchievementBase(BaseModel):
    title: str = Field(..., min_length=2)
    description: Optional[str] = None
    date_achieved: Optional[date] = None

class AchievementCreate(AchievementBase):
    pass

class AchievementResponse(AchievementBase):
    id: int
    badge_url: Optional[str] = None
    
    class Config:
        from_attributes = True

# ----------------- Social Links -----------------
class SocialLinkBase(BaseModel):
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    leetcode_url: Optional[str] = None
    hackerrank_url: Optional[str] = None
    codechef_url: Optional[str] = None
    codeforces_url: Optional[str] = None

class SocialLinkCreate(SocialLinkBase):
    pass

class SocialLinkResponse(SocialLinkBase):
    class Config:
        from_attributes = True

# ----------------- Learning Preferences -----------------
class LearningPreferenceBase(BaseModel):
    preferred_programming_language: Optional[str] = None
    study_hours_per_day: Optional[int] = Field(None, ge=0, le=24)
    target_company: Optional[str] = None
    email_notifications: bool = True
    push_notifications: bool = True
    theme: str = "SYSTEM"

class LearningPreferenceCreate(LearningPreferenceBase):
    pass

class LearningPreferenceResponse(LearningPreferenceBase):
    class Config:
        from_attributes = True

# ----------------- Dashboard Summary -----------------
class DashboardSummaryResponse(BaseModel):
    profile_completion_percentage: int
    current_xp: int
    level: int
    streak_days: int
    study_hours: int
    coding_problems_solved: int
    projects_completed: int
    certificates_earned: int
    placement_readiness_score: int
