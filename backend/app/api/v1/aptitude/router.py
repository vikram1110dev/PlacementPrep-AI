from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import io

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
def create_question(q_data: QuestionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = AptitudeService(db)
    question = service.create_question(q_data, user_id=current_user.id)
    return StandardResponse(success=True, message="Question created successfully", data={"id": question.id})

@router.put("/questions/{question_id}", response_model=StandardResponse, dependencies=[Depends(RoleChecker(["ADMIN", "SUPER_ADMIN"]))])
def update_question(question_id: str, q_data: QuestionCreate, db: Session = Depends(get_db)):
    service = AptitudeService(db)
    question = service.update_question(question_id, q_data)
    return StandardResponse(success=True, message="Question updated", data={"id": question.id})

@router.delete("/questions/{question_id}", response_model=StandardResponse, dependencies=[Depends(RoleChecker(["ADMIN", "SUPER_ADMIN"]))])
def delete_question(question_id: str, db: Session = Depends(get_db)):
    service = AptitudeService(db)
    result = service.delete_question(question_id)
    return StandardResponse(success=True, message=result["message"])

@router.delete("/questions/{question_id}/hard", response_model=StandardResponse, dependencies=[Depends(RoleChecker(["ADMIN", "SUPER_ADMIN"]))])
def hard_delete_question(question_id: str, db: Session = Depends(get_db)):
    service = AptitudeService(db)
    result = service.hard_delete_question(question_id)
    return StandardResponse(success=True, message=result["message"])

@router.patch("/questions/{question_id}/restore", response_model=StandardResponse, dependencies=[Depends(RoleChecker(["ADMIN", "SUPER_ADMIN"]))])
def restore_question(question_id: str, db: Session = Depends(get_db)):
    service = AptitudeService(db)
    result = service.restore_question(question_id)
    return StandardResponse(success=True, message=result["message"])

@router.patch("/questions/{question_id}/status", response_model=StandardResponse, dependencies=[Depends(RoleChecker(["ADMIN", "SUPER_ADMIN"]))])
def toggle_question_status(question_id: str, is_active: bool, db: Session = Depends(get_db)):
    service = AptitudeService(db)
    question = service.toggle_question_status(question_id, is_active)
    return StandardResponse(success=True, message="Question status updated", data={"id": question.id, "is_active": question.is_active})

@router.post("/questions/import", response_model=StandardResponse, dependencies=[Depends(RoleChecker(["ADMIN", "SUPER_ADMIN"]))])
async def import_questions(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    content = await file.read()
    try:
        content_str = content.decode('utf-8')
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Invalid file encoding. Only UTF-8 CSV is supported.")
    
    service = AptitudeService(db)
    result = service.import_questions_from_csv(content_str, user_id=current_user.id)
    
    if not result["success"]:
        return StandardResponse(success=False, message="Import failed with errors", data={"errors": result["errors"]})
        
    return StandardResponse(success=True, message=f"Successfully imported {result['imported_count']} questions", data={"imported_count": result["imported_count"]})

@router.get("/questions/export", dependencies=[Depends(RoleChecker(["ADMIN", "SUPER_ADMIN"]))])
def export_questions(
    topic_id: Optional[int] = None, 
    difficulty: Optional[str] = None, 
    company: Optional[str] = None,
    tags: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    service = AptitudeService(db)
    filters = QuestionFilter(
        topic_id=topic_id, difficulty=difficulty, company=company, tags=tags, 
        is_active=is_active, include_deleted=False, skip=0, limit=100000
    )
    csv_data = service.export_questions_to_csv(filters)
    
    return StreamingResponse(
        iter([csv_data]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=questions_export.csv"}
    )

@router.post("/mock-tests", response_model=StandardResponse, dependencies=[Depends(RoleChecker(["ADMIN", "SUPER_ADMIN"]))])
def create_mock_test(test_data: MockTestCreate, db: Session = Depends(get_db)):
    service = AptitudeService(db)
    test = service.create_mock_test(test_data)
    return StandardResponse(success=True, message="Mock test created", data={"id": test.id})

# --- Categories & Topics ---
@router.get("/categories", response_model=StandardResponse)
def get_categories(db: Session = Depends(get_db)):
    service = AptitudeService(db)
    return StandardResponse(success=True, message="Categories fetched", data=service.get_categories())

@router.get("/topics", response_model=StandardResponse)
def get_topics(category_id: Optional[int] = None, db: Session = Depends(get_db)):
    service = AptitudeService(db)
    return StandardResponse(success=True, message="Topics fetched", data=service.get_topics(category_id))

# --- Student Routes (Questions) ---
@router.get("/questions", response_model=StandardResponse)
def get_questions_list(
    topic_id: Optional[int] = None, 
    difficulty: Optional[str] = None, 
    company: Optional[str] = None,
    tags: Optional[str] = None,
    is_active: Optional[bool] = None,
    include_deleted: bool = False,
    skip: int = 0, 
    limit: int = 20, 
    db: Session = Depends(get_db)
):
    service = AptitudeService(db)
    filters = QuestionFilter(
        topic_id=topic_id, difficulty=difficulty, company=company, tags=tags, 
        is_active=is_active, include_deleted=include_deleted, skip=skip, limit=limit
    )
    questions = service.get_questions(filters)
    return StandardResponse(success=True, message="Questions fetched", data=questions)

@router.post("/questions/search", response_model=StandardResponse)
def get_questions_search(filters: QuestionFilter, db: Session = Depends(get_db)):
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
@router.get("/history", response_model=StandardResponse)
def get_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = AptitudeService(db)
    return StandardResponse(success=True, message="History fetched", data=service.get_user_history(current_user.id))

@router.get("/progress", response_model=StandardResponse)
def get_progress(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = AptitudeService(db)
    return StandardResponse(success=True, message="Progress fetched", data=service.get_user_progress(current_user.id))

@router.get("/analytics/weak-topics", response_model=StandardResponse)
def get_weak_topics(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = AptitudeService(db)
    return StandardResponse(success=True, message="Weak topics analyzed via AI", data=service.get_weak_topics(current_user.id))
