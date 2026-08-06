from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc, and_, text
from datetime import datetime, timedelta
from typing import List, Optional

from app.models.aptitude import PracticeSession, QuestionAttempt, AptitudeQuestion, AptitudeTopic, AptitudeCategory
from app.models.users import StudentProfile, User, Achievement

class AnalyticsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_dashboard_overview(self, user_id: str) -> dict:
        # Get Student Profile
        profile = self.db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
        if not profile:
            # Create a default if missing
            profile = StudentProfile(user_id=user_id)
            self.db.add(profile)
            self.db.commit()

        # Aggregate Practice Sessions
        sessions = self.db.query(PracticeSession).filter(
            PracticeSession.user_id == user_id,
            PracticeSession.status == 'COMPLETED'
        ).all()

        total_tests = len(sessions)
        highest_score = max((s.score for s in sessions), default=0)
        
        # Aggregate Question Attempts
        attempts = self.db.query(QuestionAttempt).filter(
            QuestionAttempt.user_id == user_id,
            QuestionAttempt.selected_answer != None
        ).all()

        questions_solved = len(attempts)
        correct_answers = sum(1 for a in attempts if a.is_correct)
        wrong_answers = questions_solved - correct_answers
        
        # Calculate skipped answers
        total_questions_in_sessions = sum(s.total_questions or 0 for s in sessions)
        skipped_answers = total_questions_in_sessions - questions_solved
        if skipped_answers < 0: skipped_answers = 0

        total_time_taken = sum(a.time_taken_seconds or 0 for a in attempts)
        total_study_time_minutes = total_time_taken // 60
        
        accuracy = 0
        if questions_solved > 0:
            accuracy = (correct_answers / questions_solved) * 100
            
        avg_score = 0
        if total_tests > 0:
            avg_score = sum(s.score or 0 for s in sessions) / total_tests

        return {
            "total_tests": total_tests,
            "questions_solved": questions_solved,
            "correct_answers": correct_answers,
            "wrong_answers": wrong_answers,
            "skipped_answers": skipped_answers,
            "average_score": float(avg_score),
            "highest_score": float(highest_score),
            "current_streak": profile.streak_days or 0,
            "accuracy_percentage": float(accuracy),
            "total_study_time_minutes": total_study_time_minutes,
            "current_xp": profile.current_xp or 0,
            "level": profile.level or 1
        }

    def get_recent_activity(self, user_id: str, limit: int = 5) -> List[dict]:
        sessions = self.db.query(PracticeSession).filter(
            PracticeSession.user_id == user_id,
            PracticeSession.status == 'COMPLETED'
        ).order_by(desc(PracticeSession.ended_at)).limit(limit).all()
        
        activity = []
        for s in sessions:
            activity.append({
                "session_id": s.id,
                "score": float(s.score),
                "completed_time": s.ended_at
            })
        return activity

    def get_leaderboard(self, limit: int = 5) -> List[dict]:
        profiles = self.db.query(StudentProfile).join(User).order_by(desc(StudentProfile.current_xp)).limit(limit).all()
        board = []
        for rank, p in enumerate(profiles, start=1):
            board.append({
                "user_id": p.user_id,
                "rank": rank,
                "name": p.user.full_name or "Anonymous",
                "level": p.level or 1,
                "xp": p.current_xp or 0
            })
        return board

    def get_achievements(self, user_id: str) -> List[Achievement]:
        return self.db.query(Achievement).filter(Achievement.user_id == user_id).all()
        
    def award_xp(self, user_id: str, xp_amount: int) -> StudentProfile:
        profile = self.db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
        if profile:
            profile.current_xp = (profile.current_xp or 0) + xp_amount
            # Calculate Level (simple logic: 1 level per 500 XP)
            profile.level = (profile.current_xp // 500) + 1
            self.db.commit()
        return profile
        
    def unlock_achievement(self, user_id: str, title: str, description: str):
        # Check if already unlocked
        existing = self.db.query(Achievement).filter(
            Achievement.user_id == user_id, 
            Achievement.title == title
        ).first()
        
        if not existing:
            ach = Achievement(
                user_id=user_id,
                title=title,
                description=description,
                date_achieved=datetime.utcnow().date()
            )
            self.db.add(ach)
            self.db.commit()
            return True
        return False
        
    def get_weekly_problems_solved(self, user_id: str) -> dict:
        # Group by day of the week for the last 7 days
        # For simplicity, returning mock shaped data based on real counts
        now = datetime.utcnow()
        labels = []
        data = []
        for i in range(6, -1, -1):
            d = now - timedelta(days=i)
            labels.append(d.strftime("%A")[:3])
            
            # Count solved on this day
            count = self.db.query(QuestionAttempt).filter(
                QuestionAttempt.user_id == user_id,
                QuestionAttempt.selected_answer != None,
                func.date(QuestionAttempt.attempted_at) == d.date()
            ).count()
            data.append(float(count))
            
        return {"labels": labels, "data": data}

    def get_learning_distribution(self, user_id: str) -> dict:
        # Distribution across Categories (e.g., Quant vs Logical vs Verbal)
        # We need to join QuestionAttempt -> AptitudeQuestion -> Topic -> Category
        results = self.db.query(
            AptitudeCategory.name,
            func.count(QuestionAttempt.id)
        ).select_from(QuestionAttempt).join(
            AptitudeQuestion, QuestionAttempt.question_id == AptitudeQuestion.id
        ).join(
            AptitudeTopic, AptitudeQuestion.topic_id == AptitudeTopic.id
        ).join(
            AptitudeCategory, AptitudeTopic.category_id == AptitudeCategory.id
        ).filter(
            QuestionAttempt.user_id == user_id,
            QuestionAttempt.selected_answer != None
        ).group_by(AptitudeCategory.name).all()
        
        labels = [r[0] for r in results]
        data = [float(r[1]) for r in results]
        return {"labels": labels, "data": data}
