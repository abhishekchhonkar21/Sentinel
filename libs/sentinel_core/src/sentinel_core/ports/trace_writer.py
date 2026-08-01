"""Agent trace writer port — decouples BaseAgent from MongoDB."""

from abc import ABC, abstractmethod


class TraceWriter(ABC):
    @abstractmethod
    async def write(
        self,
        *,
        anomaly_id: str,
        agent_name: str,
        input_payload: dict,
        output_payload: dict | None,
        latency_ms: float,
        token_usage: int | None = None,
    ) -> None: ...
