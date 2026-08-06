from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.users import User
from app.services.analytics_service import AnalyticsService
from app.schemas.base import StandardResponse
from app.schemas.analytics import (
    DashboardOverviewResponse,
    LeaderboardUser,
    RecentActivity,
    ChartDataResponse,
    AchievementResponse
)
from typing import List

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/dashboard", response_model=StandardResponse)
def get_dashboard_overview(
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    svc = AnalyticsService(db)
    data = svc.get_dashboard_overview(current_user.id)
    return StandardResponse(success=True, message="Dashboard overview fetched", data=data)

@router.get("/leaderboard", response_model=StandardResponse)
def get_leaderboard(
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    svc = AnalyticsService(db)
    data = svc.get_leaderboard()
    return StandardResponse(success=True, message="Leaderboard fetched", data=[l.model_dump() for l in data])

@router.get("/recent", response_model=StandardResponse)
def get_recent_activity(
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    svc = AnalyticsService(db)
    data = svc.get_recent_activity(current_user.id)
    return StandardResponse(success=True, message="Recent activity fetched", data=[r.model_dump() for r in data])

@router.get("/achievements", response_model=StandardResponse)
def get_achievements(
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    svc = AnalyticsService(db)
    data = svc.get_achievements(current_user.id)
    return StandardResponse(success=True, message="Achievements fetched", data=[a.model_dump() for a in data])

@router.get("/weekly", response_model=StandardResponse)
def get_weekly_chart(
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    svc = AnalyticsService(db)
    data = svc.get_weekly_chart(current_user.id)
    return StandardResponse(success=True, message="Weekly chart fetched", data=data.model_dump())

@router.get("/distribution", response_model=StandardResponse)
def get_learning_distribution(
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    svc = AnalyticsService(db)
    data = svc.get_learning_dist_chart(current_user.id)
    return StandardResponse(success=True, message="Learning distribution fetched", data=data.model_dump())
