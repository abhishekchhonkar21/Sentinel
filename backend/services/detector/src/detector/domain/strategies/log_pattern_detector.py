"""Log pattern detection — regex/keyword flags + optional HF classifier (Week 5 v2)."""

from sentinel_core.ports.detection_strategy import AnomalyDetectionStrategy, DetectionWindow
from sentinel_core.schemas.contracts import AnomalyEvent


class LogPatternDetectionStrategy(AnomalyDetectionStrategy):
    strategy_name = "log_pattern"

    async def detect(self, window: DetectionWindow) -> list[AnomalyEvent]:
        # TODO: regex patterns + optional DistilBERT classifier
        return []
