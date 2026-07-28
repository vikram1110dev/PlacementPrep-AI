from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.connection import get_db
from app.dependencies.auth import get_current_user, RoleChecker
from app.models.auth import User
from app.schemas.base import StandardResponse
from app.schemas.aptitude import (
    QuestionCreate, QuestionResponse, QuestionFilter,
    MockTestCreate, MockTestResponse, MockTestSubmission, MockTestResult,
    SubmitAnswerRequest, PracticeSessionResponse
)
from app.services.aptitude_service import AptitudeService

router = APIRouter(prefix="/aptitude", tags=["Aptitude Module"])

# --- Admin Routes (CRUD Questions) ---
@router.post("/questions", response_model=StandardResponse, dependencies=[Depends(RoleChecker(["ADMIN", "SUPER_ADMIN"]))])
def create_question(q_data: QuestionCreate, db: Session = Depends(get_db)):
    service = AptitudeService(db)
    question = service.create_question(q_data)
    return StandardResponse(success=True, message="Question created successfully", data={"id": question.id})

@router.post("/mock-tests", response_model=StandardResponse, dependencies=[Depends(RoleChecker(["ADMIN", "SUPER_ADMIN"]))])
def create_mock_test(test_data: MockTestCreate, db: Session = Depends(get_db)):
    service = AptitudeService(db)
    test = service.create_mock_test(test_data)
    return StandardResponse(success=True, message="Mock test created", data={"id": test.id})

# --- Student Routes ---
@router.post("/questions/search", response_model=StandardResponse)
def get_questions(filters: QuestionFilter, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = AptitudeService(db)
    questions = service.get_questions(filters)
    return StandardResponse(success=True, message="Questions fetched", data=questions)

# --- Practice ---
@router.post("/practice/start", response_model=StandardResponse)
def start_practice(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = AptitudeService(db)
    session = service.start_practice(current_user.id)
    return StandardResponse(success=True, message="Practice started", data={"session_id": session.id, "started_at": session.started_at})

@router.post("/practice/{session_id}/submit", response_model=StandardResponse)
def submit_practice_answer(session_id: str, answer_data: SubmitAnswerRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = AptitudeService(db)
    result = service.submit_practice_answer(current_user.id, session_id, answer_data)
    return StandardResponse(success=True, message="Answer evaluated", data=result)

@router.post("/practice/{session_id}/finish", response_model=StandardResponse)
def finish_practice(session_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = AptitudeService(db)
    result = service.end_practice(session_id)
    return StandardResponse(success=True, message="Practice finished", data=result)

# --- Mock Tests ---
@router.post("/mock-tests/{test_id}/submit", response_model=StandardResponse)
def submit_mock_test(test_id: int, submission: MockTestSubmission, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = AptitudeService(db)
    result = service.evaluate_mock_test(test_id, current_user.id, submission)
    return StandardResponse(success=True, message="Test evaluated successfully", data=result)

# --- Analytics ---
@router.get("/analytics/weak-topics", response_model=StandardResponse)
def get_weak_topics(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = AptitudeService(db)
    return StandardResponse(success=True, message="Weak topics analyzed via AI", data=service.get_weak_topics(current_user.id))
