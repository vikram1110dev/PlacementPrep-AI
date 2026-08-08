import pytest
from unittest.mock import patch, MagicMock
from app.services.interview_service import InterviewService
from app.schemas.interview import InterviewSetupRequest, InterviewAnswerRequest
from app.models.interview import InterviewSession, InterviewQuestion, InterviewAnswer

@pytest.fixture
def mock_db():
    db = MagicMock()
    # Mocking standard SQLAlchemy methods
    db.query.return_value.filter_by.return_value.first.return_value = None
    db.query.return_value.filter_by.return_value.order_by.return_value.all.return_value = []
    db.query.return_value.filter_by.return_value.all.return_value = []
    return db

@pytest.fixture
def mock_llm_response():
    response = MagicMock()
    response.content = '[{"question_text": "What is Python?", "expected_hints": "programming language"}]'
    return response

@patch("app.services.interview_service.get_llm")
def test_start_session(mock_get_llm, mock_db, mock_llm_response):
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = mock_llm_response
    mock_get_llm.return_value = mock_llm
    
    service = InterviewService(mock_db)
    
    request = InterviewSetupRequest(
        interview_type="technical",
        role="Software Engineer",
        company="Google",
        difficulty="medium",
        num_questions=1
    )
    
    # Mock session generation
    def side_effect_add(obj):
        if hasattr(obj, 'id') and obj.id is None:
            obj.id = "session-123"
            
    mock_db.add.side_effect = side_effect_add
    
    session = service.start_session("user-1", request)
    
    assert session.interview_type == "technical"
    assert session.role == "Software Engineer"
    assert session.status == "in_progress"
    
    # Verify llm was called
    mock_llm.invoke.assert_called()

@patch("app.services.interview_service.get_llm")
def test_evaluate_answer(mock_get_llm, mock_db):
    mock_llm = MagicMock()
    eval_response = MagicMock()
    eval_response.content = '{"score": 8.5, "feedback_good": "Good.", "feedback_missing": "None.", "feedback_improve": "None."}'
    mock_llm.invoke.return_value = eval_response
    mock_get_llm.return_value = mock_llm
    
    service = InterviewService(mock_db)
    
    # Mock finding a session and question
    mock_session = InterviewSession(id="session-123", user_id="user-1", status="in_progress")
    mock_question = InterviewQuestion(id="q-1", session_id="session-123", question_text="What is Python?", order=1)
    mock_question.answer = None
    
    mock_db.query.return_value.filter_by.return_value.first.return_value = mock_session
    mock_db.query.return_value.filter_by.return_value.order_by.return_value.all.return_value = [mock_question]
    
    req = InterviewAnswerRequest(answer_text="It is a programming language.")
    
    eval_data = service.evaluate_answer("user-1", "session-123", req)
    
    assert eval_data["score"] == 8.5
    assert eval_data["feedback_good"] == "Good."
    mock_llm.invoke.assert_called()

@patch("app.services.interview_service.get_llm")
def test_complete_session(mock_get_llm, mock_db):
    mock_llm = MagicMock()
    report_resp = MagicMock()
    report_resp.content = '{"feedback_strengths": "Great", "feedback_weaknesses": "None", "feedback_improvements": "Keep it up"}'
    mock_llm.invoke.return_value = report_resp
    mock_get_llm.return_value = mock_llm
    
    service = InterviewService(mock_db)
    
    mock_session = InterviewSession(id="session-123", user_id="user-1", status="in_progress", interview_type="technical")
    mock_answer = InterviewAnswer(score=9.0)
    mock_question = InterviewQuestion(id="q-1", answer=mock_answer)
    
    mock_db.query.return_value.filter_by.return_value.first.return_value = mock_session
    mock_db.query.return_value.filter_by.return_value.all.return_value = [mock_question]
    
    session = service.complete_session("user-1", "session-123")
    
    assert session.status == "completed"
    assert session.overall_score == 9.0
    assert session.feedback_strengths == "Great"
