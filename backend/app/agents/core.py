from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings

def get_llm(temperature: float = 0.7, streaming: bool = True):
    """
    Returns the configured LLM based on environment variables.
    Defaults to Gemini if configured, otherwise OpenAI.
    """
    if settings.GEMINI_API_KEY:
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            temperature=temperature,
            google_api_key=settings.GEMINI_API_KEY,
            streaming=streaming
        )
    elif settings.OPENAI_API_KEY:
        return ChatOpenAI(
            model="gpt-4o-mini",
            temperature=temperature,
            openai_api_key=settings.OPENAI_API_KEY,
            streaming=streaming
        )
    else:
        # Fallback dummy LLM or throw error
        raise ValueError("No LLM API keys configured. Set GEMINI_API_KEY or OPENAI_API_KEY.")
