"""Application service — orchestrates domain strategies and persistence."""

from datetime import UTC, datetime
from uuid import uuid4

from detector.domain.models import DetectRequest, DetectResponse
from detector.domain.strategies.composite_detector import CompositeDetectionStrategy
from sentinel_core.domain.enums import AgentName
from sentinel_core.ports.detection_strategy import DetectionWindow
from sentinel_core.ports.repositories import AnomalyEventRepository
from sentinel_core.ports.trace_writer import TraceWriter
from sentinel_core.schemas.contracts import AnomalyEvent


class DetectionService:
    """Application layer — coordinates detection strategies and repository writes.

    Unlike other agents, detector may emit multiple events per request;
    it does not subclass BaseAgent directly but uses the same TraceWriter port.
    """

    def __init__(
        self,
        *,
        strategy: CompositeDetectionStrategy,
        anomaly_repo: AnomalyEventRepository,
        trace_writer: TraceWriter,
    ) -> None:
        self._strategy = strategy
        self._anomaly_repo = anomaly_repo
        self._trace_writer = trace_writer

    async def detect(self, request: DetectRequest) -> DetectResponse:
        window = DetectionWindow(
            service=request.service,
            start=request.window_start,
            end=request.window_end,
            logs=request.logs,
            metrics=request.metrics,
        )
        events = await self._strategy.detect(window)
        persisted: list[AnomalyEvent] = []
        for event in events:
            if not event.anomaly_id:
                event = event.model_copy(update={"anomaly_id": str(uuid4())})
            await self._anomaly_repo.save(event)
            await self._trace_writer.write(
                anomaly_id=event.anomaly_id,
                agent_name=AgentName.DETECTOR.value,
                input_payload=request.model_dump(mode="json"),
                output_payload=event.model_dump(mode="json"),
                latency_ms=0.0,
            )
            persisted.append(event)
        return DetectResponse(events=persisted, detected_at=datetime.now(UTC))
