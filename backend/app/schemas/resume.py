from pydantic import BaseModel, HttpUrl, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import date
from decimal import Decimal

# --- Resume Internal Sections (JSON Structure) ---
class PersonalDetails(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None

class Experience(BaseModel):
    company: str
    role: str
    location: Optional[str] = None
    start_date: str
    end_date: Optional[str] = None # "Present" if None
    description: List[str]

class EducationItem(BaseModel):
    institution: str
    degree: str
    start_year: str
    end_year: Optional[str] = None
    cgpa: Optional[str] = None

class ProjectItem(BaseModel):
    title: str
    tech_stack: List[str]
    link: Optional[str] = None
    description: List[str]

class ResumeData(BaseModel):
    personal_details: PersonalDetails
    professional_summary: str
    experience: List[Experience] = []
    education: List[EducationItem] = []
    projects: List[ProjectItem] = []
    skills: List[str] = []
    certifications: List[str] = []
    achievements: List[str] = []
    custom_sections: Optional[Dict[str, Any]] = None

# --- API Payloads ---
class UserResumeCreate(BaseModel):
    title: str = Field(..., description="Name of this resume version")
    template_id: Optional[int] = None
    resume_data: ResumeData

class UserResumeUpdate(BaseModel):
    title: Optional[str] = None
    template_id: Optional[int] = None
    resume_data: Optional[ResumeData] = None
    is_primary: Optional[int] = None

class UserResumeResponse(BaseModel):
    id: str
    title: str
    is_primary: int
    template_id: Optional[int]
    resume_data: ResumeData
    
    class Config:
        from_attributes = True

# --- ATS Payload ---
class ATSReportResponse(BaseModel):
    id: str
    overall_score: Decimal
    formatting_score: Decimal
    section_completeness: Decimal
    missing_skills: List[str]
    keyword_matches: List[str]
    industry_suggestions: List[str]
    
    class Config:
        from_attributes = True
