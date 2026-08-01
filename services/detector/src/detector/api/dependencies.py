"""Service-local FastAPI dependencies — extends sentinel_core DI with detector wiring."""

from functools import lru_cache

from detector.application.detection_service import DetectionService
from detector.domain.strategies.composite_detector import CompositeDetectionStrategy
from sentinel_core.infrastructure.dependencies import get_anomaly_repository, get_trace_writer


@lru_cache
def get_detection_strategy() -> CompositeDetectionStrategy:
    return CompositeDetectionStrategy()


def get_detection_service() -> DetectionService:
    return DetectionService(
        strategy=get_detection_strategy(),
        anomaly_repo=get_anomaly_repository(),
        trace_writer=get_trace_writer(),
    )
