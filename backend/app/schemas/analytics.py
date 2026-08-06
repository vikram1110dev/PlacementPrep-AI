from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal

class DashboardOverviewResponse(BaseModel):
    total_tests: int
    questions_solved: int
    correct_answers: int
    wrong_answers: int
    skipped_answers: int
    average_score: float
    highest_score: float
    current_streak: int
    accuracy_percentage: float
    total_study_time_minutes: int
    current_xp: int
    level: int

class LeaderboardUser(BaseModel):
    user_id: str
    rank: int
    name: str
    level: int
    xp: int

class RecentActivity(BaseModel):
    session_id: str
    score: float
    completed_time: datetime
    # Optionally we could add category if it's tied to the session

class ChartDataset(BaseModel):
    label: str
    data: List[float]

class ChartDataResponse(BaseModel):
    labels: List[str]
    datasets: List[ChartDataset]

class TopicAnalyticsItem(BaseModel):
    topic_name: str
    questions_attempted: int
    correct: int
    wrong: int
    accuracy: float
    avg_time_seconds: float

class CategoryAnalyticsItem(BaseModel):
    category_name: str
    questions_solved: int
    accuracy: float
    average_score: float
    improvement_percentage: float

class AchievementResponse(BaseModel):
    title: str
    description: str
    date_achieved: date
    badge_url: Optional[str] = None
