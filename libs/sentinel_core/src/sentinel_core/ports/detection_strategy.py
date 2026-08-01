"""Detection strategy port — composite detector runs multiple strategies."""

from abc import ABC, abstractmethod
from datetime import datetime

from sentinel_core.schemas.contracts import AnomalyEvent


class DetectionWindow:
    """Value object: logs + metrics slice the detector evaluates."""

    def __init__(
        self,
        *,
        service: str,
        start: datetime,
        end: datetime,
        logs: list[str],
        metrics: dict[str, list[float]],
    ) -> None:
        self.service = service
        self.start = start
        self.end = end
        self.logs = logs
        self.metrics = metrics


class AnomalyDetectionStrategy(ABC):
    """Strategy pattern — statistical, regex, HF classifier each subclass this."""

    strategy_name: str = "base"

    @abstractmethod
    async def detect(self, window: DetectionWindow) -> list[AnomalyEvent]:
        """Return zero or more anomaly events with confidence scores."""
