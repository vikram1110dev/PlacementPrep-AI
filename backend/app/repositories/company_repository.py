from sqlalchemy.orm import Session
from sqlalchemy import func
import random
from app.models.admin import Company
from app.models.company_prep import CompanyPattern, CompanyPreviousYearStats
from app.models.aptitude import AptitudeQuestion, company_question_tags, PracticeSession, QuestionAttempt

class CompanyRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_active_companies(self):
        return self.db.query(Company).filter(Company.is_active == True).all()

    def get_company_by_id(self, company_id: int):
        return self.db.query(Company).filter(Company.id == company_id).first()

    def get_company_stats(self, company_id: int):
        return self.db.query(CompanyPreviousYearStats).filter(CompanyPreviousYearStats.company_id == company_id).first()

    def get_company_patterns(self, company_id: int):
        return self.db.query(CompanyPattern).filter(CompanyPattern.company_id == company_id).all()

    def get_pattern_by_id(self, pattern_id: int):
        return self.db.query(CompanyPattern).filter(CompanyPattern.id == pattern_id).first()

    def get_questions_for_company(self, company_id: int, limit: int = 50):
        # We query AptitudeQuestions that are linked to this company via the M:N table
        # Since we might not have many questions mapped properly in the current db,
        # we will fallback to all active questions if we can't find enough, just so the test engine doesn't break during demo.
        questions = self.db.query(AptitudeQuestion).join(
            company_question_tags, 
            AptitudeQuestion.id == company_question_tags.c.question_id
        ).filter(
            company_question_tags.c.company_id == company_id,
            AptitudeQuestion.is_active == True
        ).all()

        if len(questions) < limit:
            # Fallback for demo: just fetch random active questions
            fallback_qs = self.db.query(AptitudeQuestion).filter(
                AptitudeQuestion.is_active == True
            ).limit(limit).all()
            
            # Merge and deduplicate
            questions_dict = {q.id: q for q in questions}
            for q in fallback_qs:
                if len(questions_dict) >= limit: break
                questions_dict[q.id] = q
            questions = list(questions_dict.values())

        if len(questions) > limit:
            questions = random.sample(questions, limit)
            
        return questions

    def create_company_test_session(self, user_id: str, company_id: int, pattern: CompanyPattern):
        # 1. Create a practice session
        session = PracticeSession(
            user_id=user_id,
            total_questions=pattern.total_questions
        )
        self.db.add(session)
        self.db.flush() # get session.id

        # 2. Get questions
        questions = self.get_questions_for_company(company_id, pattern.total_questions)

        # 3. Create attempts
        for q in questions:
            attempt = QuestionAttempt(
                session_id=session.id,
                user_id=user_id,
                question_id=q.id
            )
            self.db.add(attempt)
        
        self.db.commit()
        return session
