from sqlalchemy.orm import Session, joinedload
from sqlalchemy import exc
from typing import Optional, List

from app.models.auth import User
from app.models.users import (
    StudentProfile, Education, Skill, StudentSkill, 
    Certificate, Achievement, SocialLink, LearningPreference
)
from app.schemas.users import (
    StudentProfileCreate, EducationCreate, StudentSkillAdd,
    CertificateCreate, AchievementCreate, SocialLinkCreate, LearningPreferenceCreate
)

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    # --- Profile ---
    def get_student_profile(self, user_id: str) -> Optional[StudentProfile]:
        return self.db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()

    def update_student_profile(self, user_id: str, profile_data: dict) -> StudentProfile:
        profile = self.get_student_profile(user_id)
        if not profile:
            profile = StudentProfile(user_id=user_id)
            self.db.add(profile)
        
        for key, value in profile_data.items():
            if value is not None:
                setattr(profile, key, value)
                
        self.db.commit()
        self.db.refresh(profile)
        return profile

    # --- Education ---
    def get_education(self, user_id: str) -> List[Education]:
        return self.db.query(Education).filter(Education.user_id == user_id).all()
        
    def add_education(self, user_id: str, edu_data: EducationCreate) -> Education:
        edu = Education(user_id=user_id, **edu_data.model_dump())
        self.db.add(edu)
        self.db.commit()
        self.db.refresh(edu)
        return edu

    def delete_education(self, user_id: str, edu_id: int) -> bool:
        edu = self.db.query(Education).filter(Education.id == edu_id, Education.user_id == user_id).first()
        if edu:
            self.db.delete(edu)
            self.db.commit()
            return True
        return False

    # --- Skills ---
    def get_available_skills(self) -> List[Skill]:
        return self.db.query(Skill).all()

    def get_student_skills(self, user_id: str) -> List[StudentSkill]:
        return self.db.query(StudentSkill).options(joinedload(StudentSkill.skill)).filter(StudentSkill.user_id == user_id).all()

    def add_student_skill(self, user_id: str, skill_data: StudentSkillAdd) -> StudentSkill:
        # Check if exists
        existing = self.db.query(StudentSkill).filter(
            StudentSkill.user_id == user_id, 
            StudentSkill.skill_id == skill_data.skill_id
        ).first()
        
        if existing:
            existing.proficiency = skill_data.proficiency
            self.db.commit()
            self.db.refresh(existing)
            return existing
            
        new_skill = StudentSkill(user_id=user_id, **skill_data.model_dump())
        self.db.add(new_skill)
        self.db.commit()
        self.db.refresh(new_skill)
        return new_skill
        
    def remove_student_skill(self, user_id: str, skill_id: int) -> bool:
        skill = self.db.query(StudentSkill).filter(StudentSkill.user_id == user_id, StudentSkill.skill_id == skill_id).first()
        if skill:
            self.db.delete(skill)
            self.db.commit()
            return True
        return False

    # --- Certificates ---
    def get_certificates(self, user_id: str) -> List[Certificate]:
        return self.db.query(Certificate).filter(Certificate.user_id == user_id).all()
        
    def add_certificate(self, user_id: str, cert_data: CertificateCreate) -> Certificate:
        cert = Certificate(user_id=user_id, **cert_data.model_dump())
        self.db.add(cert)
        self.db.commit()
        self.db.refresh(cert)
        return cert

    # --- Achievements ---
    def get_achievements(self, user_id: str) -> List[Achievement]:
        return self.db.query(Achievement).filter(Achievement.user_id == user_id).all()
        
    def add_achievement(self, user_id: str, ach_data: AchievementCreate) -> Achievement:
        ach = Achievement(user_id=user_id, **ach_data.model_dump())
        self.db.add(ach)
        self.db.commit()
        self.db.refresh(ach)
        return ach

    # --- Social Links ---
    def get_social_links(self, user_id: str) -> Optional[SocialLink]:
        return self.db.query(SocialLink).filter(SocialLink.user_id == user_id).first()

    def update_social_links(self, user_id: str, links_data: dict) -> SocialLink:
        links = self.get_social_links(user_id)
        if not links:
            links = SocialLink(user_id=user_id)
            self.db.add(links)
        
        for key, value in links_data.items():
            if value is not None:
                setattr(links, key, value)
                
        self.db.commit()
        self.db.refresh(links)
        return links

    # --- Learning Preferences ---
    def get_preferences(self, user_id: str) -> Optional[LearningPreference]:
        return self.db.query(LearningPreference).filter(LearningPreference.user_id == user_id).first()

    def update_preferences(self, user_id: str, pref_data: dict) -> LearningPreference:
        pref = self.get_preferences(user_id)
        if not pref:
            pref = LearningPreference(user_id=user_id)
            self.db.add(pref)
        
        for key, value in pref_data.items():
            if value is not None:
                setattr(pref, key, value)
                
        self.db.commit()
        self.db.refresh(pref)
        return pref
