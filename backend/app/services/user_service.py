from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.schemas.users import (
    StudentProfileCreate, EducationCreate, StudentSkillAdd,
    CertificateCreate, AchievementCreate, SocialLinkCreate, LearningPreferenceCreate,
    DashboardSummaryResponse
)

class UserService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def calculate_profile_completion(self, user_id: str) -> int:
        score = 0
        total_fields = 7
        
        if self.repo.get_student_profile(user_id): score += 1
        if self.repo.get_education(user_id): score += 1
        if self.repo.get_student_skills(user_id): score += 1
        if self.repo.get_certificates(user_id): score += 1
        if self.repo.get_achievements(user_id): score += 1
        if self.repo.get_social_links(user_id): score += 1
        if self.repo.get_preferences(user_id): score += 1
        
        return int((score / total_fields) * 100)

    def get_dashboard_summary(self, user_id: str) -> dict:
        profile = self.repo.get_student_profile(user_id)
        
        # Safe access with fallback values if profile doesn't exist yet
        xp = profile.current_xp if profile else 0
        level = profile.level if profile else 1
        streak = profile.streak_days if profile else 0
        readiness = profile.placement_score if profile else 0
        
        # These are dummy/mocked values for modules not yet implemented
        # (DSA, Projects, Coding)
        coding_solved = 120 if profile else 0
        projects_comp = 3 if profile else 0
        study_hours = 45 if profile else 0
        
        certs = len(self.repo.get_certificates(user_id))

        return {
            "profile_completion_percentage": self.calculate_profile_completion(user_id),
            "current_xp": xp,
            "level": level,
            "streak_days": streak,
            "study_hours": study_hours,
            "coding_problems_solved": coding_solved,
            "projects_completed": projects_comp,
            "certificates_earned": certs,
            "placement_readiness_score": readiness
        }

    # Profile logic
    def update_profile(self, user_id: str, profile_data: StudentProfileCreate):
        return self.repo.update_student_profile(user_id, profile_data.model_dump(exclude_unset=True))
        
    def get_profile(self, user_id: str):
        return self.repo.get_student_profile(user_id)

    # Education
    def add_education(self, user_id: str, edu_data: EducationCreate):
        return self.repo.add_education(user_id, edu_data)

    def get_education(self, user_id: str):
        return self.repo.get_education(user_id)

    # Skills
    def add_skill(self, user_id: str, skill_data: StudentSkillAdd):
        return self.repo.add_student_skill(user_id, skill_data)

    def get_skills(self, user_id: str):
        return self.repo.get_student_skills(user_id)

    # Certificates
    def add_certificate(self, user_id: str, cert_data: CertificateCreate):
        return self.repo.add_certificate(user_id, cert_data)
        
    def get_certificates(self, user_id: str):
        return self.repo.get_certificates(user_id)

    # Achievements
    def add_achievement(self, user_id: str, ach_data: AchievementCreate):
        return self.repo.add_achievement(user_id, ach_data)
        
    def get_achievements(self, user_id: str):
        return self.repo.get_achievements(user_id)

    # Social Links
    def update_social_links(self, user_id: str, links_data: SocialLinkCreate):
        return self.repo.update_social_links(user_id, links_data.model_dump(exclude_unset=True))
        
    def get_social_links(self, user_id: str):
        return self.repo.get_social_links(user_id)

    # Preferences
    def update_preferences(self, user_id: str, pref_data: LearningPreferenceCreate):
        return self.repo.update_preferences(user_id, pref_data.model_dump(exclude_unset=True))
        
    def get_preferences(self, user_id: str):
        return self.repo.get_preferences(user_id)
