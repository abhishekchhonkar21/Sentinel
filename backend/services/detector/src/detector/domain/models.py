"""Detector-specific request/response DTOs — API layer models, not domain entities."""

from datetime import datetime

from pydantic import BaseModel

from sentinel_core.schemas.contracts import AnomalyEvent


class DetectRequest(BaseModel):
    service: str
    window_start: datetime
    window_end: datetime
    logs: list[str]
    metrics: dict[str, list[float]]


class DetectResponse(BaseModel):
    events: list[AnomalyEvent]
    detected_at: datetime
