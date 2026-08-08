import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.connection import Base
from app.models.auth import User
from app.models.roadmap import Roadmap, RoadmapWeek, RoadmapTask
from app.schemas.roadmap import RoadmapSetupRequest, TaskStatusUpdateRequest
from app.services.roadmap_service import RoadmapService

@pytest.fixture(scope="module")
def engine():
    return create_engine("sqlite:///:memory:")

@pytest.fixture(scope="module")
def tables(engine):
    import app.models.company_prep
    import app.models.aptitude
    import app.models.auth
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture
def db_session(engine, tables):
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()
    session.close()

@pytest.fixture
def test_user(db_session):
    import uuid
    user_id = str(uuid.uuid4())
    user = User(id=user_id, email=f"test_{user_id}@test.com", hashed_password="hash", full_name="Test User")
    db_session.add(user)
    db_session.commit()
    return user

@patch("app.services.roadmap_service.AnalyticsService")
@patch("app.services.roadmap_service.AptitudeService")
@patch("app.services.roadmap_service.get_llm")
def test_generate_roadmap(mock_get_llm, mock_apt_svc, mock_ana_svc, db_session, test_user):
    # Setup mocks
    mock_llm_instance = MagicMock()
    mock_llm_instance.invoke.return_value = MagicMock(content="Mocked AI Summary.")
    mock_get_llm.return_value = mock_llm_instance

    mock_ana_instance = MagicMock()
    mock_ana_instance.get_dashboard_overview.return_value = {"questions_solved": 5}
    mock_ana_svc.return_value = mock_ana_instance

    mock_apt_instance = MagicMock()
    mock_apt_instance.get_user_progress.return_value = {"overall_accuracy": 30, "weakest_topic": "Ratio"}
    mock_apt_svc.return_value = mock_apt_instance

    service = RoadmapService(db_session)
    request = RoadmapSetupRequest(
        target_role="Data Scientist",
        target_company="Google",
        duration_weeks=2,
        daily_time_minutes=60
    )

    roadmap = service.generate_roadmap(test_user.id, request)
    
    assert roadmap is not None
    assert roadmap.target_role == "Data Scientist"
    assert roadmap.duration_weeks == 2
    assert roadmap.ai_recommendation_summary == "Mocked AI Summary."
    assert len(roadmap.weeks) == 2
    
    # 5 days per week
    assert len(roadmap.weeks[0].tasks) == 5

@patch("app.services.roadmap_service.AnalyticsService")
@patch("app.services.roadmap_service.AptitudeService")
@patch("app.services.roadmap_service.get_llm")
def test_get_current_roadmap_and_progress(mock_get_llm, mock_apt_svc, mock_ana_svc, db_session, test_user):
    service = RoadmapService(db_session)
    
    mock_llm_instance = MagicMock()
    mock_llm_instance.invoke.return_value = MagicMock(content="Mock")
    mock_get_llm.return_value = mock_llm_instance
    
    mock_ana_instance = MagicMock()
    mock_ana_instance.get_dashboard_overview.return_value = {"questions_solved": 5}
    mock_ana_svc.return_value = mock_ana_instance

    mock_apt_instance = MagicMock()
    mock_apt_instance.get_user_progress.return_value = {"overall_accuracy": 30, "weakest_topic": "Ratio"}
    mock_apt_svc.return_value = mock_apt_instance
    
    req = RoadmapSetupRequest(target_role="SDE", duration_weeks=1, daily_time_minutes=60)
    service.generate_roadmap(test_user.id, req)
    
    current = service.get_current_roadmap(test_user.id)
    assert current is not None
    assert current.completion_percentage == 0.0
    assert current.total_tasks == 5
    assert current.tasks_completed == 0

    # Complete a task
    task_id = current.weeks[0].tasks[0].id
    update_req = TaskStatusUpdateRequest(status="completed")
    service.update_task_status(test_user.id, task_id, update_req)
    
    current_updated = service.get_current_roadmap(test_user.id)
    assert current_updated.completion_percentage == 20.0
    assert current_updated.tasks_completed == 1
