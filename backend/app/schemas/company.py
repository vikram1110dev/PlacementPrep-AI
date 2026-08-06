from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime

class CompanyStatsSchema(BaseModel):
    avg_package: Optional[str] = None
    competition_level: Optional[str] = None
    success_rate_percent: Optional[float] = None
    hiring_mode: Optional[str] = None

class CompanyPatternSchema(BaseModel):
    id: int
    role_name: str
    duration_minutes: int
    total_questions: int
    sections: List[Dict[str, Any]]
    difficulty_distribution: Optional[Dict[str, int]] = None

class CompanyBase(BaseModel):
    name: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    hiring_process: Optional[List[str]] = None
    industry_type: Optional[str] = None
    tier: Optional[str] = None

class CompanyResponse(CompanyBase):
    id: int
    is_active: bool
    
    # We will include these when fetching a specific company
    stats: Optional[CompanyStatsSchema] = None
    patterns: Optional[List[CompanyPatternSchema]] = None

    class Config:
        from_attributes = True

class StartCompanyTestRequest(BaseModel):
    pattern_id: int
