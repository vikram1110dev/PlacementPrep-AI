from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories.aptitude_repository import AptitudeRepository
from app.schemas.aptitude import (
    QuestionCreate, QuestionFilter, MockTestCreate, 
    MockTestSubmission, MockTestResult, SubmitAnswerRequest
)
from decimal import Decimal

class AptitudeService:
    def __init__(self, db: Session):
        self.repo = AptitudeRepository(db)

    # --- Questions ---
    def create_question(self, q_data: QuestionCreate):
        # Validate that exactly one option is correct
        correct_count = sum(1 for opt in q_data.options if opt.is_correct)
        if correct_count != 1:
            raise HTTPException(status_code=400, detail="Exactly one option must be marked as correct.")
            
        return self.repo.create_question(q_data)
        
    def get_questions(self, filters: QuestionFilter):
        return self.repo.get_questions(filters)

    # --- Practice Sessions ---
    def start_practice(self, user_id: str):
        return self.repo.create_practice_session(user_id)
        
    def end_practice(self, session_id: str):
        self.repo.end_practice_session(session_id)
        return {"message": "Practice session ended"}

    def submit_practice_answer(self, user_id: str, session_id: str, answer_data: SubmitAnswerRequest):
        question = self.repo.get_question_by_id(answer_data.question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
            
        is_correct = False
        if answer_data.selected_option_id:
            for opt in question.options:
                if opt.id == answer_data.selected_option_id and opt.is_correct:
                    is_correct = True
                    break
                    
        self.repo.log_question_attempt(
            session_id=session_id,
            user_id=user_id,
            question_id=answer_data.question_id,
            selected_option_id=answer_data.selected_option_id,
            is_correct=is_correct,
            time_taken=answer_data.time_taken_seconds
        )
        
        # Determine correct option to return
        correct_opt = next((o for o in question.options if o.is_correct), None)
        return {
            "is_correct": is_correct,
            "correct_option_id": correct_opt.id if correct_opt else None,
            "explanation": question.explanation
        }

    # --- Mock Tests ---
    def create_mock_test(self, test_data: MockTestCreate):
        return self.repo.create_mock_test(
            title=test_data.title,
            description=test_data.description,
            duration=test_data.duration_minutes,
            total_marks=test_data.total_marks,
            q_ids=test_data.question_ids
        )

    def evaluate_mock_test(self, test_id: int, user_id: str, submission: MockTestSubmission) -> MockTestResult:
        test = self.repo.get_mock_test_by_id(test_id)
        if not test:
            raise HTTPException(status_code=404, detail="Mock test not found")

        score = Decimal("0.0")
        correct = 0
        wrong = 0
        skipped = 0
        
        # Build dictionary of questions in test
        test_questions = {mtq.question.id: mtq.question for mtq in test.questions}
        
        for answer in submission.answers:
            q = test_questions.get(answer.question_id)
            if not q:
                continue # Ignore invalid question IDs
                
            if not answer.selected_option_id:
                skipped += 1
                continue
                
            is_correct = any(opt.id == answer.selected_option_id and opt.is_correct for opt in q.options)
            
            if is_correct:
                correct += 1
                score += Decimal(str(q.marks))
            else:
                wrong += 1
                score -= Decimal(str(q.negative_marks))
                
        accuracy = Decimal("0.0")
        total_attempted = correct + wrong
        if total_attempted > 0:
            accuracy = (Decimal(correct) / Decimal(total_attempted)) * Decimal("100.0")
            
        # Log attempt
        self.repo.log_mock_test_attempt(test_id, user_id, score)

        return MockTestResult(
            score=score,
            total_marks=test.total_marks,
            correct_answers=correct,
            wrong_answers=wrong,
            skipped_answers=skipped,
            accuracy_percentage=accuracy
        )

    # --- Analytics & AI Placeholders ---
    def get_weak_topics(self, user_id: str):
        # AI/Analytics Placeholder
        return [
            {"topic_name": "Time and Work", "accuracy_percentage": 35.5, "total_attempts": 20},
            {"topic_name": "Syllogism", "accuracy_percentage": 42.0, "total_attempts": 15}
        ]
