import json
from sqlalchemy.orm import Session
from decimal import Decimal
from typing import Optional
from app.models.resume import UserResume, ATSReport
from app.repositories.resume_repository import ResumeRepository
from app.agents.core import get_llm
from langchain_core.messages import SystemMessage, HumanMessage

class ATSService:
    def __init__(self, db: Session):
        self.repo = ResumeRepository(db)
        self.llm = get_llm()

    async def analyze_resume(self, resume: UserResume) -> ATSReport:
        # Determine text source
        text_to_analyze = resume.raw_text if resume.is_uploaded else json.dumps(resume.resume_data)
        if not text_to_analyze:
            raise ValueError("No text found in resume to analyze.")

        system_prompt = """You are an expert ATS (Applicant Tracking System) Analyzer.
Your task is to analyze the provided resume text and return a STRICT JSON output with the following structure:
{
    "overall_score": float (0-100),
    "formatting_score": float (0-100),
    "section_completeness": float (0-100),
    "missing_skills": ["skill1", "skill2"],
    "keyword_matches": ["keyword1", "keyword2"],
    "industry_suggestions": ["suggestion1", "suggestion2", "Missing Section: Education (if missing)"],
    "section_scores": {
        "Experience": float,
        "Education": float,
        "Skills": float,
        "Summary": float
    },
    "bullet_improvements": [
        {
            "original": "Original weak bullet text",
            "suggested": "Action + Task + Result improved bullet",
            "reason": "Why this is better"
        }
    ]
}
DO NOT include any markdown formatting like ```json ... ```, just return the raw JSON object. Evaluate strictly like a top-tier tech company ATS."""

        human_prompt = f"Resume Content:\n{text_to_analyze}"

        response = await self.llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ])

        try:
            # Clean possible markdown wrapping if the LLM disobeys
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
            
            result = json.loads(content)
        except json.JSONDecodeError:
            raise ValueError("Failed to parse AI response into JSON.")

        report = ATSReport(
            resume_id=resume.id,
            overall_score=Decimal(str(result.get("overall_score", 0))),
            formatting_score=Decimal(str(result.get("formatting_score", 0))),
            section_completeness=Decimal(str(result.get("section_completeness", 0))),
            missing_skills=result.get("missing_skills", []),
            keyword_matches=result.get("keyword_matches", []),
            industry_suggestions=result.get("industry_suggestions", []),
            section_scores=result.get("section_scores", {}),
            bullet_improvements=result.get("bullet_improvements", [])
        )
        
        return self.repo.save_ats_report(report)

    async def match_job_description(self, resume: UserResume, job_description: str) -> ATSReport:
        text_to_analyze = resume.raw_text if resume.is_uploaded else json.dumps(resume.resume_data)
        if not text_to_analyze:
            raise ValueError("No text found in resume to analyze.")

        system_prompt = """You are an expert Tech Recruiter.
Analyze the provided resume against the job description and return a STRICT JSON output:
{
    "match_percentage": float (0-100),
    "missing_skills": ["skill1", "skill2"],
    "keyword_matches": ["keyword1", "keyword2"],
    "industry_suggestions": ["Priority improvement 1", "Priority improvement 2"]
}
DO NOT include any markdown formatting, just return raw JSON."""

        human_prompt = f"Resume Content:\n{text_to_analyze}\n\nJob Description:\n{job_description}"

        response = await self.llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ])

        try:
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
            result = json.loads(content)
        except json.JSONDecodeError:
            raise ValueError("Failed to parse AI response into JSON.")

        report = ATSReport(
            resume_id=resume.id,
            overall_score=Decimal(str(result.get("match_percentage", 0))), # Repurpose overall for match
            formatting_score=None,
            section_completeness=None,
            match_percentage=Decimal(str(result.get("match_percentage", 0))),
            missing_skills=result.get("missing_skills", []),
            keyword_matches=result.get("keyword_matches", []),
            industry_suggestions=result.get("industry_suggestions", []),
            job_description=job_description
        )
        
        return self.repo.save_ats_report(report)
