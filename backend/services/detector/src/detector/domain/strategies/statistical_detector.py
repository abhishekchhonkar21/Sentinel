"""Statistical detection — z-score/EWMA on metrics (Week 4 v1)."""

from sentinel_core.ports.detection_strategy import AnomalyDetectionStrategy, DetectionWindow
from sentinel_core.schemas.contracts import AnomalyEvent


class StatisticalDetectionStrategy(AnomalyDetectionStrategy):
    strategy_name = "statistical"

    async def detect(self, window: DetectionWindow) -> list[AnomalyEvent]:
        # TODO: implement z-score/EWMA on window.metrics error_rate and latency_p99
        return []
