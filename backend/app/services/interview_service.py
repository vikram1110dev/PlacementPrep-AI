import json
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import HTTPException
from app.models.interview import InterviewSession, InterviewQuestion, InterviewAnswer
from app.schemas.interview import InterviewSetupRequest, InterviewAnswerRequest
from app.agents.core import get_llm
from langchain_core.messages import HumanMessage, SystemMessage

class InterviewService:
    def __init__(self, db: Session):
        self.db = db
        self.llm = get_llm(temperature=0.3, streaming=False) # Lower temperature for structured output

    def start_session(self, user_id: str, request: InterviewSetupRequest) -> InterviewSession:
        # Create session
        session = InterviewSession(
            user_id=user_id,
            interview_type=request.interview_type,
            role=request.role,
            company=request.company,
            difficulty=request.difficulty,
            status='in_progress'
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        # Generate questions
        prompt = f"""You are an expert interviewer. Generate exactly {request.num_questions} interview questions for a candidate.
Context:
- Interview Type: {request.interview_type}
- Target Role: {request.role}
- Target Company: {request.company or 'Generic'}
- Difficulty: {request.difficulty}

Return ONLY a valid JSON array of objects. Each object must have:
"question_text": The actual question to ask.
"expected_hints": Brief hints on what a good answer should contain.
Do not include markdown blocks like ```json. Just raw JSON.
"""
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            questions_data = json.loads(response.content.strip())
            
            for idx, q_data in enumerate(questions_data):
                q = InterviewQuestion(
                    session_id=session.id,
                    question_text=q_data.get('question_text', ''),
                    expected_answer_hints=q_data.get('expected_hints', ''),
                    order=idx + 1
                )
                self.db.add(q)
            self.db.commit()
        except Exception as e:
            # Fallback questions if generation fails
            q = InterviewQuestion(
                session_id=session.id,
                question_text=f"Tell me about yourself and your experience with {request.role}.",
                expected_answer_hints="Clear introduction, relevant experience",
                order=1
            )
            self.db.add(q)
            self.db.commit()

        return session

    def get_session_state(self, user_id: str, session_id: str):
        session = self.db.query(InterviewSession).filter_by(id=session_id, user_id=user_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Interview session not found")
        
        questions = self.db.query(InterviewQuestion).filter_by(session_id=session_id).order_by(InterviewQuestion.order).all()
        answered_questions = [q for q in questions if q.answer is not None]
        
        current_question = None
        for q in questions:
            if q.answer is None:
                current_question = q
                break
                
        is_complete = session.status == 'completed' or (current_question is None and len(questions) > 0)
        
        # Ensure we mark completed correctly
        if is_complete and session.status != 'completed':
            self.complete_session(user_id, session_id)
            session.status = 'completed'
            
        return {
            "session_id": session.id,
            "status": session.status,
            "current_question": {
                "id": current_question.id,
                "order": current_question.order,
                "question_text": current_question.question_text
            } if current_question else None,
            "total_questions": len(questions),
            "questions_answered": len(answered_questions),
            "is_complete": is_complete
        }

    def evaluate_answer(self, user_id: str, session_id: str, answer_req: InterviewAnswerRequest):
        session = self.db.query(InterviewSession).filter_by(id=session_id, user_id=user_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Interview session not found")
            
        # Get current question
        questions = self.db.query(InterviewQuestion).filter_by(session_id=session_id).order_by(InterviewQuestion.order).all()
        current_q = None
        for q in questions:
            if q.answer is None:
                current_q = q
                break
                
        if not current_q:
            raise HTTPException(status_code=400, detail="Interview already completed")

        # Call AI for evaluation
        prompt = f"""Evaluate this interview answer.
Question: {current_q.question_text}
Expected Hints: {current_q.expected_answer_hints}
Candidate Answer: {answer_req.answer_text}

Return ONLY a valid JSON object with the following fields:
"score": A float between 0 and 10 indicating overall quality.
"feedback_good": What they did well (string).
"feedback_missing": What was missing or wrong (string).
"feedback_improve": Actionable advice to improve (string).
"model_answer": A brief example of a better answer (string).
Do not include markdown blocks like ```json. Just raw JSON.
"""
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            eval_data = json.loads(response.content.strip())
        except Exception:
            eval_data = {
                "score": 5.0,
                "feedback_good": "Answer received.",
                "feedback_missing": "AI evaluation failed.",
                "feedback_improve": "N/A",
                "model_answer": None
            }

        answer = InterviewAnswer(
            question_id=current_q.id,
            user_answer=answer_req.answer_text,
            score=eval_data.get('score', 0),
            feedback_good=eval_data.get('feedback_good', ''),
            feedback_missing=eval_data.get('feedback_missing', ''),
            feedback_improve=eval_data.get('feedback_improve', ''),
            model_answer=eval_data.get('model_answer', None)
        )
        self.db.add(answer)
        self.db.commit()
        self.db.refresh(answer)
        
        return eval_data

    def complete_session(self, user_id: str, session_id: str):
        session = self.db.query(InterviewSession).filter_by(id=session_id, user_id=user_id).first()
        if not session or session.status == 'completed':
            return session
            
        questions = self.db.query(InterviewQuestion).filter_by(session_id=session_id).all()
        answers = [q.answer for q in questions if q.answer is not None]
        
        if not answers:
            session.status = 'completed'
            session.end_time = datetime.utcnow()
            self.db.commit()
            return session
            
        avg_score = sum([a.score for a in answers if a.score]) / len(answers)
        
        # Simple breakdown for MVP
        session.overall_score = avg_score
        session.technical_score = avg_score if session.interview_type in ['technical', 'mixed'] else None
        session.communication_score = avg_score
        
        # Summarize
        prompt = f"""Based on these {len(answers)} interview answers (Average Score: {avg_score}/10), provide a short summary.
Return a JSON object with:
"feedback_strengths": Key strengths (string).
"feedback_weaknesses": Key weaknesses (string).
"feedback_improvements": Recommended next steps (string).
Do not include markdown blocks like ```json. Just raw JSON.
"""
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            summary = json.loads(response.content.strip())
            session.feedback_strengths = summary.get('feedback_strengths', '')
            session.feedback_weaknesses = summary.get('feedback_weaknesses', '')
            session.feedback_improvements = summary.get('feedback_improvements', '')
        except Exception:
            pass

        session.status = 'completed'
        session.end_time = datetime.utcnow()
        self.db.commit()
        return session
