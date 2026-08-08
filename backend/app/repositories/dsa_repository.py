from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from datetime import datetime
from app.models.dsa import DSAProblem, DSATestCase, DSASubmission, DSAProgress, SubmissionStatus

class DSARepository:
    def __init__(self, db: Session):
        self.db = db

    def get_problems(self, difficulty: Optional[str] = None, category: Optional[str] = None) -> List[DSAProblem]:
        query = self.db.query(DSAProblem).filter(DSAProblem.is_active == True)
        if difficulty:
            query = query.filter(DSAProblem.difficulty == difficulty)
        if category:
            query = query.filter(DSAProblem.category.ilike(f"%{category}%"))
        return query.all()

    def get_problem_by_id(self, problem_id: str) -> Optional[DSAProblem]:
        return self.db.query(DSAProblem).filter(DSAProblem.id == problem_id).first()

    def get_test_cases(self, problem_id: str, include_hidden: bool = False) -> List[DSATestCase]:
        query = self.db.query(DSATestCase).filter(DSATestCase.problem_id == problem_id)
        if not include_hidden:
            query = query.filter(DSATestCase.is_hidden == False)
        return query.all()

    def get_test_case_by_id(self, test_case_id: str) -> Optional[DSATestCase]:
        return self.db.query(DSATestCase).filter(DSATestCase.id == test_case_id).first()

    def get_user_progress(self, user_id: str) -> DSAProgress:
        progress = self.db.query(DSAProgress).filter(DSAProgress.user_id == user_id).first()
        if not progress:
            progress = DSAProgress(user_id=user_id)
            self.db.add(progress)
            self.db.commit()
            self.db.refresh(progress)
        return progress

    def update_progress(self, user_id: str, difficulty: str, is_new_solve: bool = True):
        progress = self.get_user_progress(user_id)
        if is_new_solve:
            progress.total_solved += 1
            if difficulty == 'easy':
                progress.easy_solved += 1
            elif difficulty == 'medium':
                progress.medium_solved += 1
            elif difficulty == 'hard':
                progress.hard_solved += 1
            
            # naive streak calculation (just bumps it for demo if they solve today)
            today = datetime.utcnow().date()
            if progress.last_solved_date:
                if progress.last_solved_date.date() < today:
                    progress.current_streak += 1
            else:
                progress.current_streak = 1
                
            progress.last_solved_date = datetime.utcnow()
            
        self.db.commit()
        self.db.refresh(progress)

    def save_submission(
        self, user_id: str, problem_id: str, language: str, code: str,
        status: SubmissionStatus, passed_tests: int, total_tests: int,
        execution_time: float = None, memory_usage: float = None, error_message: str = None
    ) -> DSASubmission:
        
        # Check if user already solved it to know if this is a "new" solve
        prev_solve = self.db.query(DSASubmission).filter(
            DSASubmission.user_id == user_id,
            DSASubmission.problem_id == problem_id,
            DSASubmission.status == SubmissionStatus.ACCEPTED
        ).first()

        submission = DSASubmission(
            user_id=user_id,
            problem_id=problem_id,
            language=language,
            code=code,
            status=status,
            passed_tests=passed_tests,
            total_tests=total_tests,
            execution_time=execution_time,
            memory_usage=memory_usage,
            error_message=error_message
        )
        self.db.add(submission)
        
        # Increment attempt counter
        progress = self.get_user_progress(user_id)
        progress.total_attempted += 1

        # If it's accepted and they haven't solved it before
        if status == SubmissionStatus.ACCEPTED and not prev_solve:
            problem = self.get_problem_by_id(problem_id)
            if problem:
                self.update_progress(user_id, problem.difficulty.value, is_new_solve=True)

        self.db.commit()
        self.db.refresh(submission)
        return submission

    def get_user_problem_status(self, user_id: str, problem_id: str) -> str:
        submissions = self.db.query(DSASubmission).filter(
            DSASubmission.user_id == user_id, 
            DSASubmission.problem_id == problem_id
        ).all()
        
        if not submissions:
            return "Not Attempted"
        
        if any(s.status == SubmissionStatus.ACCEPTED for s in submissions):
            return "Solved"
            
        return "Attempted"

    def get_user_submissions(self, user_id: str, limit: int = 50) -> List[DSASubmission]:
        return self.db.query(DSASubmission).filter(
            DSASubmission.user_id == user_id
        ).order_by(DSASubmission.submitted_at.desc()).limit(limit).all()

    def get_submission_by_id(self, submission_id: str, user_id: str) -> Optional[DSASubmission]:
        return self.db.query(DSASubmission).filter(
            DSASubmission.id == submission_id,
            DSASubmission.user_id == user_id
        ).first()

    def get_recommendations(self, user_id: str) -> List[dict]:
        progress = self.get_user_progress(user_id)
        
        # Rule 1: If haven't solved much, recommend Easy arrays/strings
        if progress.total_solved < 5:
            recs = self.db.query(DSAProblem).filter(
                DSAProblem.is_active == True,
                DSAProblem.difficulty == 'easy'
            ).limit(3).all()
            return [{"problem": p, "reason": "Great starting point for beginners"} for p in recs]

        # Rule 2: Recommend Medium if Easy > 10 and Medium < 5
        if progress.easy_solved > 10 and progress.medium_solved < 5:
            recs = self.db.query(DSAProblem).filter(
                DSAProblem.is_active == True,
                DSAProblem.difficulty == 'medium'
            ).limit(3).all()
            return [{"problem": p, "reason": "Ready to level up to Medium difficulty"} for p in recs]

        # Rule 3: Find unattempted problems in popular categories
        # For simplicity in this demo, just return some random unattempted active problems
        # In a real app we'd join with submissions to exclude solved ones
        solved_subquery = self.db.query(DSASubmission.problem_id).filter(
            DSASubmission.user_id == user_id,
            DSASubmission.status == SubmissionStatus.ACCEPTED
        ).subquery()
        
        recs = self.db.query(DSAProblem).filter(
            DSAProblem.is_active == True,
            DSAProblem.id.notin_(solved_subquery)
        ).limit(3).all()
        
        return [{"problem": p, "reason": "Practice a new concept"} for p in recs]
