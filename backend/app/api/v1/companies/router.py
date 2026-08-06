from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.users import User
from app.services.company_service import CompanyService
from app.schemas.base import StandardResponse
from app.schemas.company import CompanyResponse, StartCompanyTestRequest
from typing import List

router = APIRouter(prefix="/companies", tags=["Companies"])

@router.get("", response_model=StandardResponse)
def get_all_companies(db: Session = Depends(get_db)):
    svc = CompanyService(db)
    companies = svc.get_companies()
    return StandardResponse(success=True, message="Companies fetched", data=[c.__dict__ for c in companies])

@router.get("/{company_id}", response_model=StandardResponse)
def get_company_details(company_id: int, db: Session = Depends(get_db)):
    svc = CompanyService(db)
    company = svc.get_company_profile(company_id)
    return StandardResponse(success=True, message="Company fetched", data=company.model_dump())

@router.post("/{company_id}/test/start", response_model=StandardResponse)
def start_company_test(
    company_id: int, 
    request: StartCompanyTestRequest,
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    svc = CompanyService(db)
    session = svc.start_test(current_user.id, company_id, request.pattern_id)
    return StandardResponse(
        success=True, 
        message="Test started", 
        data={"session_id": session.id, "total_questions": session.total_questions}
    )
