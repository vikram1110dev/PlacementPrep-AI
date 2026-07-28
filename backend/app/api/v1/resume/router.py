from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io

from app.database.connection import get_db
from app.dependencies.auth import get_current_user
from app.models.auth import User
from app.schemas.base import StandardResponse
from app.schemas.resume import UserResumeCreate, UserResumeUpdate, UserResumeResponse, ATSReportResponse
from app.repositories.resume_repository import ResumeRepository
from app.services.ats_service import ATSService
from app.services.export_service import ExportService

router = APIRouter(prefix="/resume", tags=["Resume Builder"])

@router.post("", response_model=StandardResponse)
def create_resume(payload: UserResumeCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    repo = ResumeRepository(db)
    resume = repo.create_resume(current_user.id, payload)
    return StandardResponse(success=True, message="Resume created", data={"id": resume.id})

@router.get("", response_model=StandardResponse)
def get_resumes(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    repo = ResumeRepository(db)
    resumes = repo.get_resumes_for_user(current_user.id)
    return StandardResponse(success=True, message="Resumes fetched", data=resumes)

@router.put("/{resume_id}", response_model=StandardResponse)
def update_resume(resume_id: str, payload: UserResumeUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    repo = ResumeRepository(db)
    resume = repo.update_resume(resume_id, current_user.id, payload)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return StandardResponse(success=True, message="Resume updated")

@router.delete("/{resume_id}", response_model=StandardResponse)
def delete_resume(resume_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    repo = ResumeRepository(db)
    success = repo.delete_resume(resume_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Resume not found")
    return StandardResponse(success=True, message="Resume deleted")

# --- ATS Engine ---
@router.post("/{resume_id}/ats-score", response_model=StandardResponse)
def calculate_ats_score(resume_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    repo = ResumeRepository(db)
    resume = repo.get_resume_by_id(resume_id, current_user.id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    ats_service = ATSService(db)
    report = ats_service.calculate_score(resume)
    return StandardResponse(success=True, message="ATS Scored", data={"overall_score": report.overall_score})

# --- PDF/DOCX Export ---
@router.post("/{resume_id}/pdf")
def export_pdf(resume_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    repo = ResumeRepository(db)
    resume = repo.get_resume_by_id(resume_id, current_user.id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    pdf_bytes = ExportService.generate_pdf(resume)
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=resume_{resume_id}.pdf"}
    )

@router.post("/{resume_id}/docx")
def export_docx(resume_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    repo = ResumeRepository(db)
    resume = repo.get_resume_by_id(resume_id, current_user.id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    docx_bytes = ExportService.generate_docx(resume)
    return StreamingResponse(
        io.BytesIO(docx_bytes),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename=resume_{resume_id}.docx"}
    )
