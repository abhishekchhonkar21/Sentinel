"""Gemini LLM adapter — fallback LLMProvider implementation."""

from sentinel_core.ports.llm_provider import LLMProvider, TSchema


class GeminiLLMProvider(LLMProvider):
    def __init__(self, api_key: str, *, model: str = "gemini-2.0-flash") -> None:
        self._api_key = api_key
        self._model = model

    async def complete_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[TSchema],
    ) -> TSchema:
        raise NotImplementedError("Wire google.genai client here")

    async def complete_text(self, *, system_prompt: str, user_prompt: str) -> str:
        raise NotImplementedError("Wire google.genai client here")
