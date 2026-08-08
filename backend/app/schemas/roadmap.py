from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class RoadmapSetupRequest(BaseModel):
    target_role: str = Field(..., description="e.g., Software Developer")
    target_company: Optional[str] = Field(None, description="e.g., Google, Amazon")
    duration_weeks: int = Field(4, ge=1, le=12)
    daily_time_minutes: int = Field(60, ge=30, le=300)

class RoadmapTaskResponse(BaseModel):
    id: str
    day_number: int
    topic: str
    activity: str
    estimated_time: int
    difficulty: Optional[str]
    expected_outcome: Optional[str]
    status: str

    class Config:
        from_attributes = True

class RoadmapWeekResponse(BaseModel):
    id: str
    week_number: int
    focus_area: Optional[str]
    tasks: List[RoadmapTaskResponse]

    class Config:
        from_attributes = True

class RoadmapResponse(BaseModel):
    id: str
    target_role: str
    target_company: Optional[str]
    duration_weeks: int
    daily_time_minutes: int
    ai_recommendation_summary: Optional[str]
    version: int
    is_active: bool
    created_at: datetime
    weeks: List[RoadmapWeekResponse] = []
    
    # Progress fields computed at runtime
    completion_percentage: float = 0.0
    tasks_completed: int = 0
    total_tasks: int = 0

    class Config:
        from_attributes = True

class TaskStatusUpdateRequest(BaseModel):
    status: str = Field(..., description="completed, skipped, or not_started")
