"""Groq LLM adapter — implements LLMProvider port."""

from pydantic import BaseModel

from sentinel_core.core.exceptions import LLMOutputError, ExternalServiceError
from sentinel_core.ports.llm_provider import LLMProvider, TSchema


class GroqLLMProvider(LLMProvider):
    def __init__(self, api_key: str, *, model: str = "llama-3.1-8b-instant") -> None:
        self._api_key = api_key
        self._model = model

    async def complete_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[TSchema],
    ) -> TSchema:
        # TODO: call groq SDK, parse JSON, validate with response_model
        raise NotImplementedError("Wire groq.AsyncGroq client here")

    async def complete_text(self, *, system_prompt: str, user_prompt: str) -> str:
        raise NotImplementedError("Wire groq.AsyncGroq client here")
