import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.connection import Base
from app.services.ai_service import AIService
from app.schemas.ai import ConversationCreate
from fastapi import HTTPException

# Setup in-memory sqlite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    # Load all models for Base to know about them
    import app.models.auth
    import app.models.ai
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def mock_user_id():
    return "user-123"

@pytest.fixture
def ai_service(db_session):
    with patch('app.services.ai_service.get_llm') as mock_get_llm:
        mock_llm = AsyncMock()
        mock_llm.ainvoke.return_value = MagicMock(content="Mocked response")
        mock_get_llm.return_value = mock_llm
        service = AIService(db_session)
        service.llm = mock_llm # inject mock
        return service

def test_create_conversation(ai_service, mock_user_id):
    data = ConversationCreate(title="Test", mode="aptitude")
    conv = ai_service.create_conversation(mock_user_id, data)
    assert conv.id is not None
    assert conv.title == "Test"
    assert conv.mode == "aptitude"
    assert conv.user_id == mock_user_id

def test_get_conversations(ai_service, mock_user_id):
    data = ConversationCreate(title="Test", mode="aptitude")
    ai_service.create_conversation(mock_user_id, data)
    convs = ai_service.get_conversations(mock_user_id)
    assert len(convs) == 1

def test_get_conversation_unauthorized(ai_service, mock_user_id):
    data = ConversationCreate(title="Test", mode="aptitude")
    conv = ai_service.create_conversation(mock_user_id, data)
    with pytest.raises(HTTPException) as exc:
        ai_service.get_conversation("wrong-user", conv.id)
    assert exc.value.status_code == 404

def test_delete_conversation(ai_service, mock_user_id):
    data = ConversationCreate(title="Test", mode="aptitude")
    conv = ai_service.create_conversation(mock_user_id, data)
    ai_service.delete_conversation(mock_user_id, conv.id)
    convs = ai_service.get_conversations(mock_user_id)
    assert len(convs) == 0

@pytest.mark.asyncio
async def test_chat_generator_non_streaming(ai_service, mock_user_id):
    data = ConversationCreate(title="Test", mode="aptitude")
    conv = ai_service.create_conversation(mock_user_id, data)
    
    # Mocking build_user_context to avoid DB queries for aptitude stats in tests
    with patch.object(ai_service, 'build_user_context', return_value="Mocked Context"):
        res = await ai_service.chat_generator(mock_user_id, conv.id, "Hello", stream=False)
        assert res == "Mocked response"
        
        # Verify messages saved
        db_conv = ai_service.get_conversation(mock_user_id, conv.id)
        assert len(db_conv.messages) == 2
        assert db_conv.messages[0].role == "user"
        assert db_conv.messages[1].role == "ai"
        assert db_conv.messages[1].content == "Mocked response"
