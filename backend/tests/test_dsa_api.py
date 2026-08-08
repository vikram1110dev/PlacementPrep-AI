import pytest
import asyncio
import uuid
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.connection import Base
from app.models.auth import User
from app.models.dsa import DSAProblem, DSATestCase, DSASubmission, SubmissionStatus
import app.models.users  # Fix mapper initialization

from sqlalchemy.pool import StaticPool

@pytest.fixture(scope="module")
def engine():
    return create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

@pytest.fixture(scope="module")
def tables(engine):
    import app.models.ai
    import app.models.auth
    import app.models.aptitude
    import app.models.company_prep
    import app.models.dsa
    import app.models.interview
    import app.models.resume
    import app.models.roadmap
    import app.models.users
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
    user_id = str(uuid.uuid4())
    user = User(id=user_id, email=f"test_{user_id}@test.com", hashed_password="hash", full_name="Test User")
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def app_with_db(db_session):
    from main import app
    from app.database.connection import get_db
    
    def override_get_db():
        yield db_session
        
    app.dependency_overrides[get_db] = override_get_db
    yield app
    app.dependency_overrides.clear()

@pytest.fixture
def client(app_with_db, test_user):
    # Mock get_current_user to return test_user
    from app.dependencies.auth import get_current_user
    app_with_db.dependency_overrides[get_current_user] = lambda: test_user
    return TestClient(app_with_db)

def test_get_problems(client, db_session, test_user):
    # Setup problems
    p = DSAProblem(title="Test", slug="test", description="desc", difficulty="easy", category="Arrays")
    db_session.add(p)
    db_session.commit()
    
    response = client.get("/api/v1/dsa/problems")
    assert response.status_code == 200
    assert response.json()["success"] is True
    data = response.json()["data"]
    assert len(data) >= 1
    assert data[0]["status"] == "Not Attempted"

def test_get_recommendations(client, db_session, test_user):
    response = client.get("/api/v1/dsa/recommendations")
    assert response.status_code == 200
    assert response.json()["success"] is True

def test_get_submissions(client, db_session, test_user):
    response = client.get("/api/v1/dsa/submissions")
    assert response.status_code == 200
    assert response.json()["success"] is True

def test_run_code_api(client, db_session, test_user):
    # Setup problem
    p = DSAProblem(title="Test", slug="test-run", description="desc", difficulty="easy", category="Arrays")
    db_session.add(p)
    db_session.commit()

    with patch("app.api.v1.dsa.router.DSAService") as mock_dsa_service:
        mock_instance = MagicMock()
        async def mock_run(*args, **kwargs):
            from app.schemas.dsa import ExecutionResult
            return ExecutionResult(status="Accepted", passed=True, output="1")
        
        mock_instance.run_code = mock_run
        mock_dsa_service.return_value = mock_instance

        response = client.post(
            f"/api/v1/dsa/problems/{p.id}/run",
            json={"language": "python", "code": "print(1)"}
        )
        
        assert response.status_code == 200
        assert response.json()["data"]["passed"] is True
