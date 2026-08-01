"""Base agent — Template Method pattern for all pipeline stages."""

from abc import ABC, abstractmethod
import time
from typing import Generic, TypeVar

from pydantic import BaseModel

from sentinel_core.core.exceptions import ValidationError
from sentinel_core.ports.trace_writer import TraceWriter

TInput = TypeVar("TInput", bound=BaseModel)
TOutput = TypeVar("TOutput", bound=BaseModel)


class BaseAgent(ABC, Generic[TInput, TOutput]):
    """Template Method: validate → execute → persist → trace.

    Every agent service (Detector, Investigator, Ranker, Narrator, Critic)
    subclasses this and implements only _execute(). Cross-cutting concerns
    (tracing, latency metrics, error normalization) stay in the base class.
    """

    agent_name: str = "base_agent"

    def __init__(self, trace_writer: TraceWriter) -> None:
        self._trace_writer = trace_writer

    async def run(self, payload: TInput, *, anomaly_id: str) -> TOutput:
        """Public entry point — never override; extend via hooks instead."""
        started = time.perf_counter()
        self._validate_input(payload)
        result: TOutput | None = None
        try:
            result = await self._execute(payload)
            await self._after_execute(payload, result, anomaly_id=anomaly_id)
        except Exception as exc:
            await self._on_error(payload, exc, anomaly_id=anomaly_id)
            raise
        finally:
            elapsed_ms = (time.perf_counter() - started) * 1000
            await self._trace_writer.write(
                anomaly_id=anomaly_id,
                agent_name=self.agent_name,
                input_payload=payload.model_dump(mode="json"),
                output_payload=result.model_dump(mode="json") if result else None,
                latency_ms=elapsed_ms,
            )
        assert result is not None
        return result

    def _validate_input(self, payload: TInput) -> None:
        """Override for agent-specific validation beyond Pydantic parsing."""
        if payload is None:
            raise ValidationError(f"{self.agent_name} received empty input")

    @abstractmethod
    async def _execute(self, payload: TInput) -> TOutput:
        """Core agent logic — the only method subclasses must implement."""

    async def _after_execute(
        self, payload: TInput, result: TOutput, *, anomaly_id: str
    ) -> None:
        """Hook: persist output, emit domain events. Override as needed."""

    async def _on_error(self, payload: TInput, exc: Exception, *, anomaly_id: str) -> None:
        """Hook: structured error logging before re-raise."""
