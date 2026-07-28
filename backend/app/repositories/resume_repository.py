from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.resume import UserResume, ResumeTemplate, ATSReport
from app.schemas.resume import UserResumeCreate, UserResumeUpdate

class ResumeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_resumes_for_user(self, user_id: str) -> List[UserResume]:
        return self.db.query(UserResume).filter(UserResume.user_id == user_id).all()

    def get_resume_by_id(self, resume_id: str, user_id: str) -> Optional[UserResume]:
        return self.db.query(UserResume).filter(
            UserResume.id == resume_id, 
            UserResume.user_id == user_id
        ).first()

    def create_resume(self, user_id: str, payload: UserResumeCreate) -> UserResume:
        resume = UserResume(
            user_id=user_id,
            title=payload.title,
            template_id=payload.template_id,
            resume_data=payload.resume_data.model_dump()
        )
        self.db.add(resume)
        self.db.commit()
        self.db.refresh(resume)
        return resume

    def update_resume(self, resume_id: str, user_id: str, payload: UserResumeUpdate) -> Optional[UserResume]:
        resume = self.get_resume_by_id(resume_id, user_id)
        if not resume:
            return None
            
        update_data = payload.model_dump(exclude_unset=True)
        if 'resume_data' in update_data:
            resume.resume_data = update_data['resume_data']
            del update_data['resume_data']
            
        for key, value in update_data.items():
            setattr(resume, key, value)
            
        self.db.commit()
        self.db.refresh(resume)
        return resume

    def delete_resume(self, resume_id: str, user_id: str) -> bool:
        resume = self.get_resume_by_id(resume_id, user_id)
        if resume:
            self.db.delete(resume)
            self.db.commit()
            return True
        return False

    def save_ats_report(self, report: ATSReport):
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report
