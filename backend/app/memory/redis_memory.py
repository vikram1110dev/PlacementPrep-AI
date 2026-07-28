from langchain_community.chat_message_histories import RedisChatMessageHistory
from app.core.config import settings

class MemoryManager:
    @staticmethod
    def get_session_history(session_id: str):
        """Retrieves or creates a Redis-backed conversation history."""
        redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
        # For local fallback if Redis is not running in dev:
        try:
            return RedisChatMessageHistory(session_id, url=redis_url)
        except Exception:
            # Fallback to ephemeral memory if Redis is unavailable
            from langchain_community.chat_message_histories import ChatMessageHistory
            return ChatMessageHistory()
