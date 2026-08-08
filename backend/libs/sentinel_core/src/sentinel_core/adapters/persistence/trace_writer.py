"""MongoDB implementation of TraceWriter."""

from datetime import UTC, datetime

from sentinel_core.adapters.persistence.mongo_client import get_database
from sentinel_core.domain.enums import CollectionName
from sentinel_core.ports.trace_writer import TraceWriter


class MongoTraceWriter(TraceWriter):
    def __init__(self) -> None:
        self._collection = get_database()[CollectionName.AGENT_TRACES.value]

    async def write(
        self,
        *,
        anomaly_id: str,
        agent_name: str,
        input_payload: dict,
        output_payload: dict | None,
        latency_ms: float,
        token_usage: int | None = None,
    ) -> None:
        await self._collection.insert_one(
            {
                "anomaly_id": anomaly_id,
                "agent_name": agent_name,
                "input": input_payload,
                "output": output_payload,
                "timestamp": datetime.now(UTC).isoformat(),
                "latency_ms": latency_ms,
                "token_usage": token_usage,
            }
        )
