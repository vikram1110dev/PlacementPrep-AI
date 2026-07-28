from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from app.database.connection import get_db
from app.dependencies.auth import get_current_user
from app.models.auth import User
from app.schemas.base import StandardResponse
from app.schemas.users import (
    StudentProfileCreate, StudentProfileResponse,
    EducationCreate, EducationResponse,
    StudentSkillAdd, StudentSkillResponse,
    CertificateCreate, CertificateResponse,
    AchievementCreate, AchievementResponse,
    SocialLinkCreate, SocialLinkResponse,
    LearningPreferenceCreate, LearningPreferenceResponse,
    DashboardSummaryResponse
)
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users & Profiles"])

# --- Dashboard & Me ---
@router.get("/me", response_model=StandardResponse)
def get_dashboard_summary(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Returns the Dashboard Summary for the currently logged in student."""
    service = UserService(db)
    summary = service.get_dashboard_summary(current_user.id)
    return StandardResponse(success=True, message="Dashboard Summary", data=summary)

# --- Profile ---
@router.get("/profile", response_model=StandardResponse)
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = UserService(db)
    profile = service.get_profile(current_user.id)
    return StandardResponse(success=True, message="Profile fetched", data=profile)

@router.put("/profile", response_model=StandardResponse)
def update_profile(profile_data: StudentProfileCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = UserService(db)
    profile = service.update_profile(current_user.id, profile_data)
    return StandardResponse(success=True, message="Profile updated successfully", data=profile)

@router.post("/profile/photo", response_model=StandardResponse)
def upload_profile_photo(file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Placeholder for actual S3/Local file upload logic
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Only JPEG or PNG are allowed")
    if file.size and file.size > 2 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (Max 2MB)")
    
    fake_url = f"/uploads/profiles/{current_user.id}_{file.filename}"
    return StandardResponse(success=True, message="Profile photo uploaded", data={"profile_photo_url": fake_url})

# --- Education ---
@router.get("/education", response_model=StandardResponse)
def get_education(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = UserService(db)
    return StandardResponse(success=True, message="Education fetched", data=service.get_education(current_user.id))

@router.post("/education", response_model=StandardResponse)
def add_education(edu_data: EducationCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = UserService(db)
    return StandardResponse(success=True, message="Education added", data=service.add_education(current_user.id, edu_data))

# --- Skills ---
@router.get("/skills", response_model=StandardResponse)
def get_skills(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = UserService(db)
    return StandardResponse(success=True, message="Skills fetched", data=service.get_skills(current_user.id))

@router.post("/skills", response_model=StandardResponse)
def add_skill(skill_data: StudentSkillAdd, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = UserService(db)
    return StandardResponse(success=True, message="Skill updated", data=service.add_skill(current_user.id, skill_data))

# --- Certificates ---
@router.get("/certificates", response_model=StandardResponse)
def get_certificates(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = UserService(db)
    return StandardResponse(success=True, message="Certificates fetched", data=service.get_certificates(current_user.id))

@router.post("/certificates", response_model=StandardResponse)
def add_certificate(cert_data: CertificateCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = UserService(db)
    return StandardResponse(success=True, message="Certificate added", data=service.add_certificate(current_user.id, cert_data))

# --- Achievements ---
@router.get("/achievements", response_model=StandardResponse)
def get_achievements(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = UserService(db)
    return StandardResponse(success=True, message="Achievements fetched", data=service.get_achievements(current_user.id))

@router.post("/achievements", response_model=StandardResponse)
def add_achievement(ach_data: AchievementCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = UserService(db)
    return StandardResponse(success=True, message="Achievement added", data=service.add_achievement(current_user.id, ach_data))

# --- Social Links ---
@router.get("/social-links", response_model=StandardResponse)
def get_social_links(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = UserService(db)
    return StandardResponse(success=True, message="Links fetched", data=service.get_social_links(current_user.id))

@router.put("/social-links", response_model=StandardResponse)
def update_social_links(links_data: SocialLinkCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = UserService(db)
    return StandardResponse(success=True, message="Links updated", data=service.update_social_links(current_user.id, links_data))

# --- Preferences ---
@router.get("/preferences", response_model=StandardResponse)
def get_preferences(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = UserService(db)
    return StandardResponse(success=True, message="Preferences fetched", data=service.get_preferences(current_user.id))

@router.put("/preferences", response_model=StandardResponse)
def update_preferences(pref_data: LearningPreferenceCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = UserService(db)
    return StandardResponse(success=True, message="Preferences updated", data=service.update_preferences(current_user.id, pref_data))
