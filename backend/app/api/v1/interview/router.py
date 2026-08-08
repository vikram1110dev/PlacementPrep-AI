from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.dependencies.auth import get_current_user
from app.models.auth import User
from app.models.interview import InterviewSession
from app.schemas.base import StandardResponse
from app.schemas.interview import (
    InterviewSetupRequest, InterviewAnswerRequest, 
    InterviewEvaluationResponse, InterviewSessionStateResponse,
    InterviewReportResponse
)
from app.services.interview_service import InterviewService

router = APIRouter(prefix="/interview", tags=["Mock Interview"])

@router.post("/start", response_model=StandardResponse)
def start_interview(request: InterviewSetupRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = InterviewService(db)
    session = service.start_session(current_user.id, request)
    return StandardResponse(success=True, message="Interview started", data={"session_id": session.id})

@router.get("/{session_id}", response_model=StandardResponse)
def get_interview_state(session_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = InterviewService(db)
    state = service.get_session_state(current_user.id, session_id)
    return StandardResponse(success=True, message="Session state retrieved", data=state)

@router.post("/{session_id}/answer", response_model=StandardResponse)
def answer_question(session_id: str, request: InterviewAnswerRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = InterviewService(db)
    evaluation = service.evaluate_answer(current_user.id, session_id, request)
    state = service.get_session_state(current_user.id, session_id)
    return StandardResponse(success=True, message="Answer evaluated", data={
        "evaluation": evaluation,
        "next_state": state
    })

@router.post("/{session_id}/complete", response_model=StandardResponse)
def complete_interview(session_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = InterviewService(db)
    service.complete_session(current_user.id, session_id)
    return StandardResponse(success=True, message="Interview completed manually", data=None)

@router.get("/{session_id}/report", response_model=StandardResponse)
def get_interview_report(session_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(InterviewSession).filter_by(id=session_id, user_id=current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    report = InterviewReportResponse(
        session_id=session.id,
        interview_type=session.interview_type,
        role=session.role,
        company=session.company,
        difficulty=session.difficulty,
        overall_score=session.overall_score,
        technical_score=session.technical_score,
        communication_score=session.communication_score,
        problem_solving_score=session.problem_solving_score,
        feedback_strengths=session.feedback_strengths,
        feedback_weaknesses=session.feedback_weaknesses,
        feedback_improvements=session.feedback_improvements,
        completed_at=session.end_time
    )
    return StandardResponse(success=True, message="Report generated", data=report.dict())

@router.get("/user/history", response_model=StandardResponse)
def get_interview_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    sessions = db.query(InterviewSession).filter_by(user_id=current_user.id).order_by(InterviewSession.start_time.desc()).all()
    history = []
    for s in sessions:
        history.append({
            "session_id": s.id,
            "interview_type": s.interview_type,
            "role": s.role,
            "company": s.company,
            "difficulty": s.difficulty,
            "status": s.status,
            "overall_score": s.overall_score,
            "start_time": s.start_time,
            "end_time": s.end_time
        })
    return StandardResponse(success=True, message="History retrieved", data=history)
