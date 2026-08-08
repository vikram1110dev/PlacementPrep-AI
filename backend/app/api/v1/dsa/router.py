from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.connection import get_db
from app.dependencies.auth import get_current_user
from app.models.auth import User
from app.schemas.base import StandardResponse
from app.schemas.dsa import (
    ProblemListResponse, 
    ProblemResponse, 
    RunCodeRequest, 
    SubmitCodeRequest, 
    DSAProgressResponse,
    ExecutionResult,
    SubmissionResultResponse
)
from app.services.dsa_service import DSAService
from app.repositories.dsa_repository import DSARepository

router = APIRouter(prefix="/dsa", tags=["DSA Practice"])

@router.get("/problems", response_model=StandardResponse)
def get_problems(
    difficulty: Optional[str] = None, 
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    dsa_service = DSAService(db)
    repo = DSARepository(db)
    
    problems = dsa_service.get_problems(difficulty, category)
    
    # Map to schema and add user status
    results = []
    for p in problems:
        status = repo.get_user_problem_status(current_user.id, p.id)
        results.append({
            "id": p.id,
            "title": p.title,
            "slug": p.slug,
            "difficulty": p.difficulty.value,
            "category": p.category,
            "status": status
        })
        
    return StandardResponse(success=True, message="Problems fetched", data=results)

@router.get("/problems/{problem_id}", response_model=StandardResponse)
def get_problem(problem_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    dsa_service = DSAService(db)
    problem = dsa_service.get_problem(problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
        
    # Include sample test cases
    sample_tests = dsa_service.get_sample_test_cases(problem_id)
    
    data = {
        "id": problem.id,
        "title": problem.title,
        "slug": problem.slug,
        "description": problem.description,
        "difficulty": problem.difficulty.value,
        "category": problem.category,
        "time_limit": problem.time_limit,
        "memory_limit": problem.memory_limit,
        "starter_code": problem.starter_code,
        "is_active": problem.is_active,
        "test_cases": [{"id": tc.id, "input_data": tc.input_data, "expected_output": tc.expected_output, "is_hidden": tc.is_hidden} for tc in sample_tests]
    }
    return StandardResponse(success=True, message="Problem fetched", data=data)

@router.post("/problems/{problem_id}/run", response_model=StandardResponse)
async def run_code(
    problem_id: str, 
    payload: RunCodeRequest, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    if len(payload.code) > 50000:
        raise HTTPException(status_code=400, detail="Source code too large")
        
    dsa_service = DSAService(db)
    try:
        result = await dsa_service.run_code(
            user_id=current_user.id,
            problem_id=problem_id,
            language=payload.language,
            code=payload.code,
            test_case_id=payload.test_case_id
        )
        return StandardResponse(success=True, message="Code executed", data=result.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution Failed: {str(e)}")

@router.post("/problems/{problem_id}/submit", response_model=StandardResponse)
async def submit_code(
    problem_id: str, 
    payload: SubmitCodeRequest, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    if len(payload.code) > 50000:
        raise HTTPException(status_code=400, detail="Source code too large")

    dsa_service = DSAService(db)
    try:
        result = await dsa_service.submit_code(
            user_id=current_user.id,
            problem_id=problem_id,
            language=payload.language,
            code=payload.code
        )
        return StandardResponse(success=True, message="Code submitted", data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Submission Failed: {str(e)}")

@router.get("/progress", response_model=StandardResponse)
def get_progress(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    repo = DSARepository(db)
    progress = repo.get_user_progress(current_user.id)
    data = {
        "total_solved": progress.total_solved,
        "easy_solved": progress.easy_solved,
        "medium_solved": progress.medium_solved,
        "hard_solved": progress.hard_solved,
        "current_streak": progress.current_streak
    }
    return StandardResponse(success=True, message="Progress fetched", data=data)

@router.get("/submissions", response_model=StandardResponse)
def get_submissions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    dsa_service = DSAService(db)
    submissions = dsa_service.get_user_submissions(current_user.id)
    results = []
    for s in submissions:
        results.append({
            "id": s.id,
            "problem_id": s.problem_id,
            "problem_title": s.problem.title if s.problem else "Unknown",
            "language": s.language,
            "status": s.status.value,
            "passed_tests": s.passed_tests,
            "total_tests": s.total_tests,
            "submitted_at": s.submitted_at
        })
    return StandardResponse(success=True, message="Submissions fetched", data=results)

@router.get("/submissions/{submission_id}", response_model=StandardResponse)
def get_submission_detail(submission_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    dsa_service = DSAService(db)
    s = dsa_service.get_submission(submission_id, current_user.id)
    if not s:
        raise HTTPException(status_code=404, detail="Submission not found")
        
    data = {
        "id": s.id,
        "problem_id": s.problem_id,
        "problem_title": s.problem.title if s.problem else "Unknown",
        "language": s.language,
        "status": s.status.value,
        "passed_tests": s.passed_tests,
        "total_tests": s.total_tests,
        "submitted_at": s.submitted_at,
        "code": s.code,
        "execution_time": s.execution_time,
        "memory_usage": s.memory_usage,
        "error_message": s.error_message
    }
    return StandardResponse(success=True, message="Submission fetched", data=data)

@router.get("/recommendations", response_model=StandardResponse)
def get_recommendations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    dsa_service = DSAService(db)
    recs = dsa_service.get_recommendations(current_user.id)
    
    results = []
    for r in recs:
        p = r["problem"]
        results.append({
            "id": p.id,
            "title": p.title,
            "difficulty": p.difficulty.value,
            "category": p.category,
            "reason": r["reason"]
        })
        
    return StandardResponse(success=True, message="Recommendations fetched", data=results)
