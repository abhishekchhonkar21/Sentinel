"""Unit tests for sentinel_core Pydantic contracts."""

from sentinel_core.domain.enums import SignalType
from sentinel_core.schemas.contracts import AnomalyEvent
from datetime import UTC, datetime


def test_anomaly_event_schema():
    event = AnomalyEvent(
        anomaly_id="test-1",
        service="payments-service",
        signal_type=SignalType.LOG_PATTERN,
        confidence=0.91,
        detected_at=datetime.now(UTC),
        raw_evidence_ref="logs/window/1",
    )
    assert event.service == "payments-service"
