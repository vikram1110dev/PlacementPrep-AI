from sqlalchemy.orm import Session
from decimal import Decimal
from app.models.resume import UserResume, ATSReport
from app.repositories.resume_repository import ResumeRepository

class ATSService:
    def __init__(self, db: Session):
        self.repo = ResumeRepository(db)

    def calculate_score(self, resume: UserResume) -> ATSReport:
        data = resume.resume_data
        
        score = 0
        completeness = 0
        
        # Check completeness
        sections_present = 0
        total_sections = 5 # Details, Summary, Edu, Exp, Skills
        
        if data.get("personal_details"): sections_present += 1
        if data.get("professional_summary"): sections_present += 1
        if data.get("education"): sections_present += 1
        if data.get("experience"): sections_present += 1
        if data.get("skills"): sections_present += 1
            
        completeness = (sections_present / total_sections) * 100
        
        # Mock calculation
        formatting = 85.0
        overall = (completeness * 0.6) + (formatting * 0.4)
        
        report = ATSReport(
            resume_id=resume.id,
            overall_score=Decimal(str(overall)),
            formatting_score=Decimal(str(formatting)),
            section_completeness=Decimal(str(completeness)),
            missing_skills=["Kubernetes", "AWS"],
            keyword_matches=["Python", "FastAPI"],
            industry_suggestions=["Add more quantified achievements."]
        )
        
        return self.repo.save_ats_report(report)
