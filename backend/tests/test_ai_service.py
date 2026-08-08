import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.database.connection import Base
from app.models.auth import User
from app.models.ai import Conversation, Message
from app.schemas.ai import ConversationCreate
from app.services.ai_service import AIService
import uuid

@pytest.fixture(scope="module")
def engine():
    return create_engine("sqlite:///:memory:")

@pytest.fixture(scope="module")
def tables(engine):
    # Import all models to ensure they are registered with Base
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
def test_user_2(db_session):
    user_id = str(uuid.uuid4())
    user = User(id=user_id, email=f"test_{user_id}@test.com", hashed_password="hash", full_name="Test User 2")
    db_session.add(user)
    db_session.commit()
    return user

@patch("app.services.ai_service.get_llm")
def test_create_and_list_conversations(mock_get_llm, db_session, test_user, test_user_2):
    mock_get_llm.return_value = MagicMock()
    service = AIService(db_session)
    
    # Create conversation for user 1
    req = ConversationCreate(title="Test Chat", mode="general")
    conv = service.create_conversation(test_user.id, req)
    
    assert conv.title == "Test Chat"
    assert conv.user_id == test_user.id
    
    # List conversations for user 1
    convs = service.get_conversations(test_user.id)
    assert len(convs) == 1
    assert convs[0].id == conv.id
    
    # List conversations for user 2 (should be empty, IDOR check)
    convs2 = service.get_conversations(test_user_2.id)
    assert len(convs2) == 0

@patch("app.services.ai_service.get_llm")
def test_rename_and_delete_conversation(mock_get_llm, db_session, test_user):
    mock_get_llm.return_value = MagicMock()
    service = AIService(db_session)
    
    req = ConversationCreate(title="Old Title", mode="dsa")
    conv = service.create_conversation(test_user.id, req)
    
    # Rename
    renamed = service.rename_conversation(test_user.id, conv.id, "New Title")
    assert renamed.title == "New Title"
    
    # Delete
    service.delete_conversation(test_user.id, conv.id)
    convs = service.get_conversations(test_user.id)
    # Filter for the deleted ID
    assert not any(c.id == conv.id for c in convs)

@patch("app.services.ai_service.get_llm")
def test_chat_non_streaming(mock_get_llm, db_session, test_user):
    # Setup mock LLM response
    import asyncio
    
    class AsyncMock(MagicMock):
        async def __call__(self, *args, **kwargs):
            return super(AsyncMock, self).__call__(*args, **kwargs)

    mock_llm_instance = MagicMock()
    mock_response = MagicMock(content="I am the AI Mentor")
    
    # Mocking an async method (ainvoke)
    async def mock_ainvoke(*args, **kwargs):
        return mock_response
        
    mock_llm_instance.ainvoke = mock_ainvoke
    mock_get_llm.return_value = mock_llm_instance

    service = AIService(db_session)
    req = ConversationCreate(title="Chat Test", mode="general")
    conv = service.create_conversation(test_user.id, req)
    
    response_text = asyncio.run(service.chat_generator(test_user.id, conv.id, "Hello", stream=False))
    
    assert response_text == "I am the AI Mentor"
    
    # Verify messages were saved
    messages = db_session.query(Message).filter(Message.conversation_id == conv.id).order_by(Message.created_at.asc()).all()
    assert len(messages) == 2
    assert messages[0].role == "user"
    assert messages[0].content == "Hello"
    assert messages[1].role == "ai"
    assert messages[1].content == "I am the AI Mentor"
