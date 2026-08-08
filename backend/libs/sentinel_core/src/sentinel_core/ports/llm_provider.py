"""LLM provider port — Strategy pattern; Groq/Gemini are interchangeable adapters."""

from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel

TSchema = TypeVar("TSchema", bound=BaseModel)


class LLMProvider(ABC):
    """Structured completion only — no open-ended reasoning prompts."""

    @abstractmethod
    async def complete_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[TSchema],
    ) -> TSchema:
        """Return parsed Pydantic model; raise LLMOutputError on invalid JSON."""

    @abstractmethod
    async def complete_text(self, *, system_prompt: str, user_prompt: str) -> str:
        """Unstructured completion for naive baseline eval only."""
