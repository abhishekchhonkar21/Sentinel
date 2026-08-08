"""Factory — primary Groq with Gemini fallback."""

from sentinel_core.adapters.llm.gemini_provider import GeminiLLMProvider
from sentinel_core.adapters.llm.groq_provider import GroqLLMProvider
from sentinel_core.config.settings import Settings
from sentinel_core.ports.llm_provider import LLMProvider


def build_llm_provider(settings: Settings | None = None) -> LLMProvider:
    settings = settings or Settings()
    if settings.llm_primary == "gemini" and settings.gemini_api_key:
        return GeminiLLMProvider(settings.gemini_api_key)
    if settings.groq_api_key:
        return GroqLLMProvider(settings.groq_api_key)
    if settings.gemini_api_key:
        return GeminiLLMProvider(settings.gemini_api_key)
    raise ValueError("No LLM API key configured (GROQ_API_KEY or GEMINI_API_KEY)")
