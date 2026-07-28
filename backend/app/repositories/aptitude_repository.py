from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime

from app.models.aptitude import (
    AptitudeCategory, AptitudeTopic, AptitudeQuestion, AptitudeOption,
    PracticeSession, QuestionAttempt, MockTest, MockTestQuestion, MockTestAttempt
)
from app.schemas.aptitude import QuestionCreate, QuestionFilter

class AptitudeRepository:
    def __init__(self, db: Session):
        self.db = db

    # --- Category & Topic ---
    def get_categories(self) -> List[AptitudeCategory]:
        return self.db.query(AptitudeCategory).all()
        
    def create_category(self, name: str) -> AptitudeCategory:
        cat = AptitudeCategory(name=name)
        self.db.add(cat)
        self.db.commit()
        self.db.refresh(cat)
        return cat

    def get_topics(self, category_id: Optional[int] = None) -> List[AptitudeTopic]:
        query = self.db.query(AptitudeTopic).options(joinedload(AptitudeTopic.category))
        if category_id:
            query = query.filter(AptitudeTopic.category_id == category_id)
        return query.all()
        
    def create_topic(self, category_id: int, name: str) -> AptitudeTopic:
        topic = AptitudeTopic(category_id=category_id, name=name)
        self.db.add(topic)
        self.db.commit()
        self.db.refresh(topic)
        return topic

    # --- Questions ---
    def create_question(self, q_data: QuestionCreate) -> AptitudeQuestion:
        # Create Question
        question = AptitudeQuestion(
            topic_id=q_data.topic_id,
            question_text=q_data.question_text,
            difficulty=q_data.difficulty,
            explanation=q_data.explanation,
            marks=q_data.marks,
            negative_marks=q_data.negative_marks,
            estimated_time_seconds=q_data.estimated_time_seconds
        )
        self.db.add(question)
        self.db.commit() # Commit to get question.id for options
        
        # Create Options
        for opt in q_data.options:
            option = AptitudeOption(
                question_id=question.id,
                option_text=opt.option_text,
                is_correct=opt.is_correct
            )
            self.db.add(option)
            
        self.db.commit()
        self.db.refresh(question)
        return question

    def get_questions(self, filters: QuestionFilter) -> List[AptitudeQuestion]:
        query = self.db.query(AptitudeQuestion).options(joinedload(AptitudeQuestion.options))
        if filters.topic_id:
            query = query.filter(AptitudeQuestion.topic_id == filters.topic_id)
        if filters.difficulty:
            query = query.filter(AptitudeQuestion.difficulty == filters.difficulty)
            
        return query.offset(filters.skip).limit(filters.limit).all()

    def get_question_by_id(self, question_id: str) -> Optional[AptitudeQuestion]:
        return self.db.query(AptitudeQuestion).options(joinedload(AptitudeQuestion.options)).filter(AptitudeQuestion.id == question_id).first()

    # --- Practice & Attempts ---
    def create_practice_session(self, user_id: str) -> PracticeSession:
        session = PracticeSession(user_id=user_id)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session
        
    def end_practice_session(self, session_id: str):
        session = self.db.query(PracticeSession).filter(PracticeSession.id == session_id).first()
        if session:
            session.ended_at = datetime.utcnow()
            self.db.commit()

    def log_question_attempt(self, session_id: str, user_id: str, question_id: str, selected_option_id: Optional[int], is_correct: bool, time_taken: int):
        attempt = QuestionAttempt(
            session_id=session_id,
            user_id=user_id,
            question_id=question_id,
            selected_option_id=selected_option_id,
            is_correct=is_correct,
            time_taken_seconds=time_taken
        )
        self.db.add(attempt)
        self.db.commit()

    # --- Mock Tests ---
    def get_mock_tests(self) -> List[MockTest]:
        return self.db.query(MockTest).all()
        
    def get_mock_test_by_id(self, test_id: int) -> MockTest:
        return self.db.query(MockTest).options(joinedload(MockTest.questions).joinedload(MockTestQuestion.question)).filter(MockTest.id == test_id).first()

    def create_mock_test(self, title: str, description: str, duration: int, total_marks: int, q_ids: List[str]) -> MockTest:
        test = MockTest(title=title, description=description, duration_minutes=duration, total_marks=total_marks)
        self.db.add(test)
        self.db.commit()
        
        for idx, q_id in enumerate(q_ids):
            mtq = MockTestQuestion(mock_test_id=test.id, question_id=q_id, order_index=idx)
            self.db.add(mtq)
            
        self.db.commit()
        self.db.refresh(test)
        return test
        
    def log_mock_test_attempt(self, test_id: int, user_id: str, score: float) -> MockTestAttempt:
        attempt = MockTestAttempt(
            mock_test_id=test_id,
            user_id=user_id,
            score=score,
            completed_at=datetime.utcnow()
        )
        self.db.add(attempt)
        self.db.commit()
        return attempt
