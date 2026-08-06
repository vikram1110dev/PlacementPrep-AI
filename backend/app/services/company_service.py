from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories.company_repository import CompanyRepository
from app.schemas.company import CompanyResponse, CompanyStatsSchema, CompanyPatternSchema

class CompanyService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = CompanyRepository(db)

    def get_companies(self):
        companies = self.repo.get_active_companies()
        return companies # We'll let the router format it into schema

    def get_company_profile(self, company_id: int):
        company = self.repo.get_company_by_id(company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        stats = self.repo.get_company_stats(company_id)
        patterns = self.repo.get_company_patterns(company_id)

        # Convert to Pydantic schema
        comp_dict = company.__dict__
        if stats:
            comp_dict["stats"] = CompanyStatsSchema(
                avg_package=stats.avg_package,
                competition_level=stats.competition_level,
                success_rate_percent=float(stats.success_rate_percent) if stats.success_rate_percent else None,
                hiring_mode=stats.hiring_mode
            )
        else:
            comp_dict["stats"] = None

        if patterns:
            comp_dict["patterns"] = [
                CompanyPatternSchema(
                    id=p.id,
                    role_name=p.role_name,
                    duration_minutes=p.duration_minutes,
                    total_questions=p.total_questions,
                    sections=p.sections,
                    difficulty_distribution=p.difficulty_distribution
                ) for p in patterns
            ]
        else:
            comp_dict["patterns"] = []

        return CompanyResponse(**comp_dict)

    def start_test(self, user_id: str, company_id: int, pattern_id: int):
        company = self.repo.get_company_by_id(company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
            
        pattern = self.repo.get_pattern_by_id(pattern_id)
        if not pattern or pattern.company_id != company_id:
            raise HTTPException(status_code=400, detail="Invalid pattern for this company")

        session = self.repo.create_company_test_session(user_id, company_id, pattern)
        if not session or session.total_questions == 0:
            raise HTTPException(status_code=400, detail="Could not generate test questions for this company")
            
        return session
