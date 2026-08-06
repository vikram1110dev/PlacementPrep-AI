from sqlalchemy.orm import Session
from app.repositories.analytics_repository import AnalyticsRepository
from app.schemas.analytics import (
    DashboardOverviewResponse, 
    LeaderboardUser, 
    RecentActivity,
    ChartDataResponse,
    ChartDataset,
    AchievementResponse
)
from app.repositories.aptitude_repository import AptitudeRepository
from loguru import logger

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AnalyticsRepository(db)
        self.apt_repo = AptitudeRepository(db)

    def get_dashboard_overview(self, user_id: str) -> DashboardOverviewResponse:
        data = self.repo.get_dashboard_overview(user_id)
        return DashboardOverviewResponse(**data)

    def get_leaderboard(self) -> list[LeaderboardUser]:
        users = self.repo.get_leaderboard(10)
        return [LeaderboardUser(**u) for u in users]

    def get_recent_activity(self, user_id: str) -> list[RecentActivity]:
        activities = self.repo.get_recent_activity(user_id, 5)
        return [RecentActivity(**a) for a in activities]

    def get_achievements(self, user_id: str) -> list[AchievementResponse]:
        achievements = self.repo.get_achievements(user_id)
        return [
            AchievementResponse(
                title=a.title,
                description=a.description,
                date_achieved=a.date_achieved,
                badge_url=a.badge_url
            ) for a in achievements
        ]

    def get_weekly_chart(self, user_id: str) -> ChartDataResponse:
        data = self.repo.get_weekly_problems_solved(user_id)
        dataset = ChartDataset(label="Problems Solved", data=data["data"])
        return ChartDataResponse(labels=data["labels"], datasets=[dataset])

    def get_learning_dist_chart(self, user_id: str) -> ChartDataResponse:
        data = self.repo.get_learning_distribution(user_id)
        # If empty, return some defaults so chart doesn't break
        if not data["labels"]:
            data = {"labels": ["Aptitude", "DSA", "Others"], "data": [0, 0, 0]}
        dataset = ChartDataset(label="Distribution", data=data["data"])
        return ChartDataResponse(labels=data["labels"], datasets=[dataset])

    def award_xp_and_achievements(self, user_id: str, session_id: str):
        """
        Evaluate a newly submitted test session to award XP and unlock achievements.
        """
        try:
            session = self.apt_repo.get_practice_session(session_id)
            if not session or session.user_id != user_id or session.status != 'COMPLETED':
                return
            
            # Base XP: 10 XP per correct answer
            correct_count = session.correct_answers or 0
            gained_xp = correct_count * 10
            
            # Perfect Test Bonus
            accuracy = session.accuracy_percentage or 0
            if accuracy == 100.0 and (session.total_questions or 0) >= 5:
                gained_xp += 50
                self.repo.unlock_achievement(
                    user_id, 
                    "Perfect Score", 
                    "Achieved 100% accuracy in a test with 5+ questions."
                )

            # Unlock "First Test" achievement
            overview = self.repo.get_dashboard_overview(user_id)
            if overview["total_tests"] == 1:
                if self.repo.unlock_achievement(user_id, "First Test", "Completed your first aptitude test!"):
                    gained_xp += 100

            # Unlock "100 Questions Solved"
            if overview["questions_solved"] >= 100:
                if self.repo.unlock_achievement(user_id, "Centurion", "Solved 100 questions."):
                    gained_xp += 100

            # Award XP
            if gained_xp > 0:
                self.repo.award_xp(user_id, gained_xp)
                logger.info(f"Awarded {gained_xp} XP to user {user_id}")

        except Exception as e:
            logger.error(f"Error in award_xp_and_achievements: {str(e)}")
