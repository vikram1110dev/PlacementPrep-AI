from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql.expression import func
from typing import List, Optional
from datetime import datetime

from app.models.aptitude import (
    AptitudeCategory, AptitudeTopic, AptitudeQuestion,
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
    def create_question(self, q_data: QuestionCreate, user_id: Optional[str] = None) -> AptitudeQuestion:
        # Create Question
        question = AptitudeQuestion(
            topic_id=q_data.topic_id,
            question_text=q_data.question_text,
            difficulty=q_data.difficulty,
            option_a=q_data.option_a,
            option_b=q_data.option_b,
            option_c=q_data.option_c,
            option_d=q_data.option_d,
            correct_answer=q_data.correct_answer,
            explanation=q_data.explanation,
            marks=q_data.marks,
            negative_marks=q_data.negative_marks,
            estimated_time_seconds=q_data.estimated_time_seconds,
            company=q_data.company,
            tags=q_data.tags,
            created_by=user_id
        )
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        return question

    def update_question(self, question_id: str, q_data: QuestionCreate) -> Optional[AptitudeQuestion]:
        question = self.db.query(AptitudeQuestion).filter(AptitudeQuestion.id == question_id).first()
        if not question:
            return None
        
        for key, value in q_data.model_dump().items():
            setattr(question, key, value)
            
        self.db.commit()
        self.db.refresh(question)
        return question
        
    def toggle_question_status(self, question_id: str, is_active: bool) -> Optional[AptitudeQuestion]:
        question = self.db.query(AptitudeQuestion).filter(AptitudeQuestion.id == question_id).first()
        if not question:
            return None
        question.is_active = is_active
        self.db.commit()
        self.db.refresh(question)
        return question
        
    def delete_question(self, question_id: str) -> bool:
        question = self.db.query(AptitudeQuestion).filter(AptitudeQuestion.id == question_id).first()
        if not question:
            return False
        question.deleted_at = datetime.utcnow()
        self.db.commit()
        return True

    def hard_delete_question(self, question_id: str) -> bool:
        question = self.db.query(AptitudeQuestion).filter(AptitudeQuestion.id == question_id).first()
        if not question:
            return False
        self.db.delete(question)
        self.db.commit()
        return True
        
    def restore_question(self, question_id: str) -> bool:
        question = self.db.query(AptitudeQuestion).filter(AptitudeQuestion.id == question_id).first()
        if not question:
            return False
        question.deleted_at = None
        self.db.commit()
        return True

    def get_questions(self, filters: QuestionFilter) -> List[AptitudeQuestion]:
        query = self.db.query(AptitudeQuestion)
        
        if not filters.include_deleted:
            query = query.filter(AptitudeQuestion.deleted_at == None)
            
        if filters.topic_id:
            query = query.filter(AptitudeQuestion.topic_id == filters.topic_id)
        if filters.difficulty:
            query = query.filter(AptitudeQuestion.difficulty == filters.difficulty)
        if filters.company:
            query = query.filter(AptitudeQuestion.company.ilike(f"%{filters.company}%"))
        if filters.tags:
            query = query.filter(AptitudeQuestion.tags.ilike(f"%{filters.tags}%"))
        if filters.is_active is not None:
            query = query.filter(AptitudeQuestion.is_active == filters.is_active)
        if filters.search:
            query = query.filter(AptitudeQuestion.question_text.ilike(f"%{filters.search}%"))
            
        return query.order_by(AptitudeQuestion.created_at.desc()).offset(filters.skip).limit(filters.limit).all()

    def get_question_by_id(self, question_id: str) -> Optional[AptitudeQuestion]:
        return self.db.query(AptitudeQuestion).filter(AptitudeQuestion.id == question_id).first()
        
    def bulk_create_questions(self, questions_data: List[dict]) -> int:
        count = 0
        for q_dict in questions_data:
            q = AptitudeQuestion(**q_dict)
            self.db.add(q)
            count += 1
        self.db.commit()
        return count

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

    def log_question_attempt(self, session_id: str, user_id: str, question_id: str, selected_answer: Optional[str], is_correct: bool, time_taken: int):
        attempt = QuestionAttempt(
            session_id=session_id,
            user_id=user_id,
            question_id=question_id,
            selected_answer=selected_answer,
            is_correct=is_correct,
            time_taken_seconds=time_taken
        )
        self.db.add(attempt)
        self.db.commit()

    # --- Test Engine ---
    def create_test_session(self, user_id: str, topic_id: Optional[int], difficulty: Optional[str], count: int) -> PracticeSession:
        query = self.db.query(AptitudeQuestion).filter(AptitudeQuestion.is_active == True, AptitudeQuestion.deleted_at == None)
        if topic_id:
            query = query.filter(AptitudeQuestion.topic_id == topic_id)
        if difficulty:
            query = query.filter(AptitudeQuestion.difficulty == difficulty)
            
        questions = query.order_by(func.random()).limit(count).all()
        
        session = PracticeSession(user_id=user_id, status='IN_PROGRESS', total_questions=len(questions))
        self.db.add(session)
        self.db.flush() # get session ID
        
        for q in questions:
            attempt = QuestionAttempt(
                session_id=session.id,
                user_id=user_id,
                question_id=q.id,
                is_correct=False
            )
            self.db.add(attempt)
            
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_test_session(self, session_id: str) -> Optional[PracticeSession]:
        return self.db.query(PracticeSession).options(
            joinedload(PracticeSession.attempts).joinedload(QuestionAttempt.question)
        ).filter(PracticeSession.id == session_id).first()

    def update_question_attempt(self, session_id: str, question_id: str, selected_answer: Optional[str], is_correct: bool, time_taken: int, visited: bool, marked: bool):
        attempt = self.db.query(QuestionAttempt).filter(
            QuestionAttempt.session_id == session_id,
            QuestionAttempt.question_id == question_id
        ).first()
        
        if attempt:
            attempt.selected_answer = selected_answer
            attempt.is_correct = is_correct
            attempt.time_taken_seconds = time_taken
            attempt.visited = visited
            attempt.marked_for_review = marked
            attempt.attempted_at = datetime.utcnow()
            self.db.commit()
            
    def finalize_test_session(self, session_id: str, score: float, accuracy: float, total_time: int):
        session = self.db.query(PracticeSession).filter(PracticeSession.id == session_id).first()
        if session:
            session.status = 'COMPLETED'
            session.ended_at = datetime.utcnow()
            session.score = score
            session.accuracy = accuracy
            session.time_taken_seconds = total_time
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

    def get_user_history(self, user_id: str) -> List[PracticeSession]:
        return self.db.query(PracticeSession).filter(
            PracticeSession.user_id == user_id,
            PracticeSession.ended_at != None
        ).order_by(PracticeSession.started_at.desc()).all()

    def get_user_progress_stats(self, user_id: str):
        sessions = self.get_user_history(user_id)
        # Detailed stats can be computed in the service, here we just return base sessions and attempts
        return sessions
