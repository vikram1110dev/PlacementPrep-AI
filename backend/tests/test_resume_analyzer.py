import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.resume_parser import ResumeParser
from app.services.ats_service import ATSService
from app.models.resume import UserResume

def test_extract_text_pdf_invalid():
    # Attempting to parse non-PDF bytes should raise ValueError
    with pytest.raises(ValueError):
        ResumeParser.extract_text(b"not a pdf", "test.pdf")

def test_extract_text_docx_invalid():
    with pytest.raises(ValueError):
        ResumeParser.extract_text(b"not a docx", "test.docx")

def test_extract_text_unsupported():
    with pytest.raises(ValueError, match="Unsupported file format"):
        ResumeParser.extract_text(b"some data", "test.txt")

@pytest.fixture
def mock_resume():
    r = UserResume(id="res-1", user_id="user-1", is_uploaded=1, raw_text="Experienced Software Engineer with Python and Java.")
    return r

@pytest.mark.asyncio
async def test_analyze_resume(mock_resume):
    with patch('app.services.ats_service.get_llm') as mock_get_llm, \
         patch('app.services.ats_service.ResumeRepository') as mock_repo_cls:
        
        mock_llm = AsyncMock()
        # Mock LLM JSON output
        mock_llm.ainvoke.return_value = MagicMock(
            content='{"overall_score": 85, "formatting_score": 90, "section_completeness": 80, "missing_skills": ["Docker"], "keyword_matches": ["Python"], "industry_suggestions": [], "section_scores": {}, "bullet_improvements": []}'
        )
        mock_get_llm.return_value = mock_llm
        
        mock_repo = mock_repo_cls.return_value
        mock_repo.save_ats_report.side_effect = lambda x: x
        
        ats = ATSService(db=MagicMock())
        ats.llm = mock_llm
        ats.repo = mock_repo
        
        report = await ats.analyze_resume(mock_resume)
        
        assert report.overall_score == 85
        assert "Docker" in report.missing_skills
        assert "Python" in report.keyword_matches

@pytest.mark.asyncio
async def test_match_job_description(mock_resume):
    with patch('app.services.ats_service.get_llm') as mock_get_llm, \
         patch('app.services.ats_service.ResumeRepository') as mock_repo_cls:
        
        mock_llm = AsyncMock()
        mock_llm.ainvoke.return_value = MagicMock(
            content='{"match_percentage": 75, "missing_skills": ["AWS"], "keyword_matches": ["Java"], "industry_suggestions": []}'
        )
        mock_get_llm.return_value = mock_llm
        
        mock_repo = mock_repo_cls.return_value
        mock_repo.save_ats_report.side_effect = lambda x: x
        
        ats = ATSService(db=MagicMock())
        ats.llm = mock_llm
        ats.repo = mock_repo
        
        report = await ats.match_job_description(mock_resume, "Looking for Java developer with AWS.")
        
        assert report.match_percentage == 75
        assert "AWS" in report.missing_skills
        assert report.job_description == "Looking for Java developer with AWS."
