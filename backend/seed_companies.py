import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import SessionLocal, Base, engine
from app.models.admin import Company
from app.models.company_prep import CompanyPattern, CompanyPreviousYearStats
from app.models.aptitude import AptitudeQuestion
from app.models.auth import User
import app.models.users

def seed():
    # Make sure tables exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    companies = [
        {
            "name": "Google",
            "description": "Product Based SDE",
            "tier": "Dream",
            "industry_type": "Product Based",
            "logo_url": "https://ui-avatars.com/api/?name=G&background=ea4335&color=fff",
            "avg_package": "15L - 40L",
            "competition": "High",
            "success": 3.0,
            "hiring_mode": "Off-Campus",
            "patterns": [
                {"role": "SDE 1", "duration": 90, "total": 2, "sections": [{"name": "Coding", "questions": 2}]}
            ]
        },
        {
            "name": "Amazon",
            "description": "Product Based SDE",
            "tier": "Dream",
            "industry_type": "Product Based",
            "logo_url": "https://ui-avatars.com/api/?name=A&background=ff9900&color=fff",
            "avg_package": "18L - 45L",
            "competition": "High",
            "success": 4.5,
            "hiring_mode": "On-Campus",
            "patterns": [
                {"role": "SDE Intern", "duration": 90, "total": 2, "sections": [{"name": "Coding", "questions": 2}]}
            ]
        },
        {
            "name": "TCS",
            "description": "Service Based Ninja/Digital",
            "tier": "Standard",
            "industry_type": "Service Based",
            "logo_url": "https://ui-avatars.com/api/?name=TCS&background=1e3a8a&color=fff",
            "avg_package": "3.3L - 7L",
            "competition": "Medium",
            "success": 30.0,
            "hiring_mode": "On-Campus",
            "patterns": [
                {"role": "Ninja", "duration": 60, "total": 10, "sections": [{"name": "Aptitude", "questions": 10}]}
            ]
        }
    ]

    for comp in companies:
        existing = db.query(Company).filter(Company.name == comp["name"]).first()
        if not existing:
            c = Company(
                name=comp["name"],
                description=comp["description"],
                tier=comp["tier"],
                industry_type=comp["industry_type"],
                logo_url=comp["logo_url"]
            )
            db.add(c)
            db.commit()
            db.refresh(c)
            
            # Stats
            s = CompanyPreviousYearStats(
                company_id=c.id,
                avg_package=comp["avg_package"],
                competition_level=comp["competition"],
                success_rate_percent=comp["success"],
                hiring_mode=comp["hiring_mode"]
            )
            db.add(s)
            
            # Patterns
            for p in comp["patterns"]:
                pat = CompanyPattern(
                    company_id=c.id,
                    role_name=p["role"],
                    duration_minutes=p["duration"],
                    total_questions=p["total"],
                    sections=p["sections"]
                )
                db.add(pat)
                
            db.commit()

    db.close()
    print("Seeded successfully!")

if __name__ == "__main__":
    seed()
