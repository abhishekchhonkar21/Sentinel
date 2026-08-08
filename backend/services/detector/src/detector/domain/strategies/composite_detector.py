"""Composite pattern — runs multiple AnomalyDetectionStrategy implementations."""

from sentinel_core.ports.detection_strategy import AnomalyDetectionStrategy, DetectionWindow
from sentinel_core.schemas.contracts import AnomalyEvent


class CompositeDetectionStrategy(AnomalyDetectionStrategy):
    """Chain-of-responsibility / composite: merge results from all registered strategies."""

    strategy_name = "composite"

    def __init__(self) -> None:
        self._strategies: list[AnomalyDetectionStrategy] = []
        # Register default strategies once implemented:
        # self.register(StatisticalDetectionStrategy())
        # self.register(LogPatternDetectionStrategy())

    def register(self, strategy: AnomalyDetectionStrategy) -> None:
        self._strategies.append(strategy)

    async def detect(self, window: DetectionWindow) -> list[AnomalyEvent]:
        results: list[AnomalyEvent] = []
        for strategy in self._strategies:
            results.extend(await strategy.detect(window))
        return results
