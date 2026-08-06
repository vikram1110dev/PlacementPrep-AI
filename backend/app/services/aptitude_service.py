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
    def create_question(self, q_data: QuestionCreate, user_id: str = None):
        return self.repo.create_question(q_data, user_id)

    def update_question(self, question_id: str, q_data: QuestionCreate):
        question = self.repo.update_question(question_id, q_data)
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        return question

    def delete_question(self, question_id: str):
        if not self.repo.delete_question(question_id):
            raise HTTPException(status_code=404, detail="Question not found")
        return {"message": "Question deleted (soft delete)"}

    def hard_delete_question(self, question_id: str):
        if not self.repo.hard_delete_question(question_id):
            raise HTTPException(status_code=404, detail="Question not found")
        return {"message": "Question permanently deleted"}

    def restore_question(self, question_id: str):
        if not self.repo.restore_question(question_id):
            raise HTTPException(status_code=404, detail="Question not found")
        return {"message": "Question restored"}

    def toggle_question_status(self, question_id: str, is_active: bool):
        question = self.repo.toggle_question_status(question_id, is_active)
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        return question
        
    def get_questions(self, filters: QuestionFilter):
        return self.repo.get_questions(filters)

    def import_questions_from_csv(self, file_content: str, user_id: str):
        import csv
        from io import StringIO
        
        f = StringIO(file_content)
        reader = csv.DictReader(f)
        
        questions_to_create = []
        errors = []
        
        required_fields = ['topic_id', 'question_text', 'difficulty', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']
        
        for idx, row in enumerate(reader, start=2): # start=2 for line number including header
            # Validation
            missing = [field for field in required_fields if not row.get(field)]
            if missing:
                errors.append(f"Row {idx}: Missing fields {', '.join(missing)}")
                continue
            
            try:
                topic_id = int(row['topic_id'])
            except ValueError:
                errors.append(f"Row {idx}: topic_id must be an integer")
                continue
                
            q_dict = {
                'topic_id': topic_id,
                'question_text': row['question_text'],
                'difficulty': row['difficulty'].upper(),
                'option_a': row['option_a'],
                'option_b': row['option_b'],
                'option_c': row['option_c'],
                'option_d': row['option_d'],
                'correct_answer': row['correct_answer'],
                'explanation': row.get('explanation'),
                'company': row.get('company'),
                'tags': row.get('tags'),
                'created_by': user_id
            }
            
            # Optional fields with defaults
            if row.get('marks'):
                try:
                    q_dict['marks'] = int(row['marks'])
                except: pass
            if row.get('negative_marks'):
                try:
                    q_dict['negative_marks'] = Decimal(row['negative_marks'])
                except: pass
            if row.get('estimated_time_seconds'):
                try:
                    q_dict['estimated_time_seconds'] = int(row['estimated_time_seconds'])
                except: pass
                
            questions_to_create.append(q_dict)
            
        if errors:
            return {"success": False, "errors": errors, "imported_count": 0}
            
        count = self.repo.bulk_create_questions(questions_to_create)
        return {"success": True, "errors": [], "imported_count": count}

    def export_questions_to_csv(self, filters: QuestionFilter) -> str:
        import csv
        from io import StringIO
        
        questions = self.repo.get_questions(filters)
        
        f = StringIO()
        if not questions:
            return ""
            
        # Define fields
        fields = ['id', 'topic_id', 'question_text', 'difficulty', 'option_a', 'option_b', 'option_c', 'option_d', 
                  'correct_answer', 'explanation', 'marks', 'negative_marks', 'estimated_time_seconds', 
                  'company', 'tags', 'is_active', 'created_at']
                  
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        
        for q in questions:
            writer.writerow({
                'id': q.id,
                'topic_id': q.topic_id,
                'question_text': q.question_text,
                'difficulty': q.difficulty.value if hasattr(q.difficulty, 'value') else q.difficulty,
                'option_a': q.option_a,
                'option_b': q.option_b,
                'option_c': q.option_c,
                'option_d': q.option_d,
                'correct_answer': q.correct_answer,
                'explanation': q.explanation,
                'marks': q.marks,
                'negative_marks': q.negative_marks,
                'estimated_time_seconds': q.estimated_time_seconds,
                'company': q.company,
                'tags': q.tags,
                'is_active': q.is_active,
                'created_at': q.created_at.isoformat() if q.created_at else ''
            })
            
        return f.getvalue()

    # --- Categories & Topics ---
    def get_categories(self):
        return self.repo.get_categories()
        
    def get_topics(self, category_id: int = None):
        return self.repo.get_topics(category_id)

    # --- Test Engine ---
    def start_test_session(self, user_id: str, request: dict):
        topic_id = request.get('topic_id')
        difficulty = request.get('difficulty')
        count = request.get('question_count', 10)
        
        session = self.repo.create_test_session(user_id, topic_id, difficulty, count)
        if session.total_questions == 0:
            raise HTTPException(status_code=400, detail="No questions found for the selected criteria.")
            
        return session

    def get_test_session(self, session_id: str, user_id: str):
        session = self.repo.get_test_session(session_id)
        if not session or session.user_id != user_id:
            raise HTTPException(status_code=404, detail="Session not found")
            
        import random
        questions = []
        for attempt in session.attempts:
            q = attempt.question
            options = [q.option_a, q.option_b, q.option_c, q.option_d]
            random.shuffle(options)
            questions.append({
                "id": q.id,
                "question_text": q.question_text,
                "options": options,
                "time_limit_seconds": q.estimated_time_seconds,
                "attempt_state": {
                    "selected_answer": attempt.selected_answer,
                    "visited": attempt.visited,
                    "marked_for_review": attempt.marked_for_review
                }
            })
            
        return {
            "session_id": session.id,
            "started_at": session.started_at,
            "status": session.status,
            "total_questions": session.total_questions,
            "questions": questions
        }

    def answer_test_question(self, session_id: str, user_id: str, request: dict):
        session = self.repo.get_test_session(session_id)
        if not session or session.user_id != user_id:
            raise HTTPException(status_code=404, detail="Session not found")
        if session.status == 'COMPLETED':
            raise HTTPException(status_code=400, detail="Test is already completed")
            
        q_id = request.get('question_id')
        selected_answer = request.get('selected_answer')
        
        attempt = next((a for a in session.attempts if a.question_id == q_id), None)
        if not attempt:
            raise HTTPException(status_code=404, detail="Question not part of this session")
            
        is_correct = False
        if selected_answer and selected_answer.strip().lower() == attempt.question.correct_answer.strip().lower():
            is_correct = True
            
        self.repo.update_question_attempt(
            session_id=session_id,
            question_id=q_id,
            selected_answer=selected_answer,
            is_correct=is_correct,
            time_taken=attempt.time_taken_seconds + request.get('time_taken_seconds', 0),
            visited=request.get('visited', True),
            marked=request.get('marked_for_review', False)
        )
        return {"message": "Answer recorded successfully"}

    def submit_test_session(self, session_id: str, user_id: str):
        session = self.repo.get_test_session(session_id)
        if not session or session.user_id != user_id:
            raise HTTPException(status_code=404, detail="Session not found")
        if session.status == 'COMPLETED':
            raise HTTPException(status_code=400, detail="Test is already completed")
            
        score = Decimal("0.0")
        correct = 0
        wrong = 0
        skipped = 0
        total_time = 0
        
        for attempt in session.attempts:
            q = attempt.question
            total_time += (attempt.time_taken_seconds or 0)
            if not attempt.selected_answer:
                skipped += 1
            elif attempt.is_correct:
                correct += 1
                score += Decimal(str(q.marks))
            else:
                wrong += 1
                score -= Decimal(str(q.negative_marks))
                
        total_attempted = correct + wrong
        accuracy = Decimal("0.0")
        if total_attempted > 0:
            accuracy = (Decimal(correct) / Decimal(total_attempted)) * Decimal("100.0")
            
        self.repo.finalize_test_session(session_id, float(score), float(accuracy), total_time)
        
        return {
            "session_id": session_id,
            "score": float(score),
            "accuracy_percentage": float(accuracy),
            "total_questions": session.total_questions,
            "correct_answers": correct,
            "wrong_answers": wrong,
            "skipped_answers": skipped,
            "time_taken_seconds": total_time
        }

    def get_test_result(self, session_id: str, user_id: str):
        session = self.repo.get_test_session(session_id)
        if not session or session.user_id != user_id:
            raise HTTPException(status_code=404, detail="Session not found")
            
        correct = 0
        wrong = 0
        skipped = 0
        
        questions = []
        for a in session.attempts:
            if not a.selected_answer: skipped += 1
            elif a.is_correct: correct += 1
            else: wrong += 1
            
            questions.append({
                "question": {
                    "text": a.question.question_text,
                    "option_a": a.question.option_a,
                    "option_b": a.question.option_b,
                    "option_c": a.question.option_c,
                    "option_d": a.question.option_d,
                    "correct_answer": a.question.correct_answer,
                    "explanation": a.question.explanation
                },
                "attempt": {
                    "selected_answer": a.selected_answer,
                    "is_correct": a.is_correct,
                    "time_taken_seconds": a.time_taken_seconds
                }
            })
            
        return {
            "session_id": session.id,
            "score": float(session.score),
            "accuracy_percentage": float(session.accuracy),
            "total_questions": session.total_questions,
            "correct_answers": correct,
            "wrong_answers": wrong,
            "skipped_answers": skipped,
            "time_taken_seconds": session.time_taken_seconds,
            "questions": questions
        }

    # --- Practice Sessions (Legacy) ---
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
        if answer_data.selected_answer and answer_data.selected_answer.strip().lower() == question.correct_answer.strip().lower():
            is_correct = True
                    
        self.repo.log_question_attempt(
            session_id=session_id,
            user_id=user_id,
            question_id=answer_data.question_id,
            selected_answer=answer_data.selected_answer,
            is_correct=is_correct,
            time_taken=answer_data.time_taken_seconds
        )
        
        return {
            "is_correct": is_correct,
            "correct_answer": question.correct_answer,
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
                
            if not answer.selected_answer:
                skipped += 1
                continue
                
            is_correct = (answer.selected_answer.strip().lower() == q.correct_answer.strip().lower())
            
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

    # --- Analytics & Progress ---
    def get_user_history(self, user_id: str):
        sessions = self.repo.get_user_history(user_id)
        history = []
        for s in sessions:
            correct = sum(1 for a in s.attempts if a.is_correct)
            total = len(s.attempts)
            acc = Decimal(correct) / Decimal(total) * 100 if total > 0 else Decimal(0)
            history.append({
                "session_id": s.id,
                "started_at": s.started_at,
                "ended_at": s.ended_at,
                "total_questions": total,
                "correct_answers": correct,
                "score": Decimal(correct), # simplified scoring for practice
                "accuracy_percentage": acc
            })
        return history

    def get_user_progress(self, user_id: str):
        sessions = self.repo.get_user_history(user_id)
        total_tests = len(sessions)
        
        total_qs = 0
        correct_qs = 0
        total_time = 0
        topic_correct = {}
        topic_total = {}
        
        for s in sessions:
            for a in s.attempts:
                total_qs += 1
                total_time += (a.time_taken_seconds or 0)
                if a.is_correct:
                    correct_qs += 1
                    
                t_name = a.question.topic.name if a.question.topic else "Unknown"
                topic_total[t_name] = topic_total.get(t_name, 0) + 1
                if a.is_correct:
                    topic_correct[t_name] = topic_correct.get(t_name, 0) + 1
                    
        overall_accuracy = Decimal(correct_qs) / Decimal(total_qs) * 100 if total_qs > 0 else Decimal(0)
        avg_score = Decimal(correct_qs) / Decimal(total_tests) if total_tests > 0 else Decimal(0)
        
        strongest = None
        weakest = None
        best_acc = -1
        worst_acc = 101
        
        for t, total in topic_total.items():
            if total >= 3: # Need at least 3 attempts to be considered
                acc = topic_correct.get(t, 0) / total
                if acc > best_acc:
                    best_acc = acc
                    strongest = t
                if acc < worst_acc:
                    worst_acc = acc
                    weakest = t

        return {
            "total_tests_taken": total_tests,
            "overall_accuracy": overall_accuracy,
            "average_score": avg_score,
            "strongest_topic": strongest,
            "weakest_topic": weakest,
            "time_spent_minutes": total_time // 60
        }

    def get_weak_topics(self, user_id: str):
        # AI/Analytics Placeholder
        return [
            {"topic_name": "Time and Work", "accuracy_percentage": 35.5, "total_attempts": 20},
            {"topic_name": "Syllogism", "accuracy_percentage": 42.0, "total_attempts": 15}
        ]
