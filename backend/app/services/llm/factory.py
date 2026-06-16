from app.config import settings
from app.services.llm.openai_provider import OpenAIProvider
from app.services.llm.gemini_provider import GeminiProvider


def get_llm_provider():
    provider = settings.LLM_PROVIDER.lower()

    if provider == "openai":
        return OpenAIProvider()

    if provider == "gemini":
        return GeminiProvider()

    raise ValueError(f"Invalid LLM_PROVIDER: {settings.LLM_PROVIDER}")