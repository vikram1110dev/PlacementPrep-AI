import io
import os
import uuid
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.dependencies.auth import get_current_user
from app.models.auth import User
from app.schemas.base import StandardResponse
from app.schemas.resume import UserResumeCreate, UserResumeUpdate, UserResumeResponse, ATSReportResponse
from app.repositories.resume_repository import ResumeRepository
from app.services.ats_service import ATSService
from app.services.export_service import ExportService
from app.services.resume_parser import ResumeParser

router = APIRouter(prefix="/resume", tags=["Resume Builder & ATS"])

UPLOAD_DIR = os.path.join(os.getcwd(), "uploads", "resumes")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- Resume Management ---

@router.post("", response_model=StandardResponse)
def create_resume(payload: UserResumeCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    repo = ResumeRepository(db)
    resume = repo.create_resume(current_user.id, payload)
    return StandardResponse(success=True, message="Resume created", data={"id": resume.id})

@router.post("/upload", response_model=StandardResponse)
def upload_resume(
    file: UploadFile = File(...), 
    title: str = Form("Uploaded Resume"), 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    if not file.filename.endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported.")
        
    file_bytes = file.file.read()
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="File is empty.")
    if len(file_bytes) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds 5MB limit.")
        
    try:
        raw_text = ResumeParser.extract_text(file_bytes, file.filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    if not raw_text or len(raw_text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Could not extract enough text from the document.")

    # Save to disk
    file_ext = os.path.splitext(file.filename)[1]
    safe_filename = f"{current_user.id}_{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    with open(file_path, "wb") as f:
        f.write(file_bytes)
        
    repo = ResumeRepository(db)
    resume = repo.create_uploaded_resume(current_user.id, title, file_path, raw_text)
    
    return StandardResponse(success=True, message="Resume uploaded successfully", data={"id": resume.id})

@router.get("", response_model=StandardResponse)
def get_resumes(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    repo = ResumeRepository(db)
    resumes = repo.get_resumes_for_user(current_user.id)
    return StandardResponse(success=True, message="Resumes fetched", data=resumes)

@router.get("/{resume_id}", response_model=StandardResponse)
def get_resume(resume_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    repo = ResumeRepository(db)
    resume = repo.get_resume_by_id(resume_id, current_user.id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return StandardResponse(success=True, message="Resume fetched", data=resume)

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
    resume = repo.get_resume_by_id(resume_id, current_user.id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    # delete file if uploaded
    if resume.is_uploaded and resume.file_path and os.path.exists(resume.file_path):
        try:
            os.remove(resume.file_path)
        except Exception as e:
            print(f"Warning: Failed to delete file {resume.file_path}: {e}")

    repo.delete_resume(resume_id, current_user.id)
    return StandardResponse(success=True, message="Resume deleted")


# --- ATS Engine & Analysis ---

@router.post("/{resume_id}/analyze", response_model=StandardResponse)
async def analyze_resume_ats(resume_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    repo = ResumeRepository(db)
    resume = repo.get_resume_by_id(resume_id, current_user.id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    ats_service = ATSService(db)
    try:
        report = await ats_service.analyze_resume(resume)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    return StandardResponse(success=True, message="Analysis complete", data=report)

class JobMatchPayload(BaseModel):
    job_description: str

@router.post("/{resume_id}/match-job", response_model=StandardResponse)
async def match_job_description(resume_id: str, payload: JobMatchPayload, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if len(payload.job_description.strip()) < 50:
        raise HTTPException(status_code=400, detail="Job description is too short.")
        
    repo = ResumeRepository(db)
    resume = repo.get_resume_by_id(resume_id, current_user.id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    ats_service = ATSService(db)
    try:
        report = await ats_service.match_job_description(resume, payload.job_description)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    return StandardResponse(success=True, message="Job Match complete", data=report)

@router.get("/{resume_id}/history", response_model=StandardResponse)
def get_ats_history(resume_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    repo = ResumeRepository(db)
    reports = repo.get_ats_history(resume_id, current_user.id)
    return StandardResponse(success=True, message="History fetched", data=reports)


# --- PDF/DOCX Export (Builder Only) ---
@router.post("/{resume_id}/pdf")
def export_pdf(resume_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    repo = ResumeRepository(db)
    resume = repo.get_resume_by_id(resume_id, current_user.id)
    if not resume or resume.is_uploaded:
        raise HTTPException(status_code=400, detail="Cannot export an uploaded resume. Only built resumes support this.")
        
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
    if not resume or resume.is_uploaded:
        raise HTTPException(status_code=400, detail="Cannot export an uploaded resume. Only built resumes support this.")
        
    docx_bytes = ExportService.generate_docx(resume)
    return StreamingResponse(
        io.BytesIO(docx_bytes),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename=resume_{resume_id}.docx"}
    )
