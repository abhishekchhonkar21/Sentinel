"""HTTP routes — thin controller layer; no business logic here."""

from fastapi import APIRouter, Depends

from detector.api.dependencies import get_detection_service
from detector.application.detection_service import DetectionService
from detector.domain.models import DetectRequest, DetectResponse

router = APIRouter(prefix="/api/v1", tags=["detector"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "detector"}


@router.post("/detect", response_model=DetectResponse)
async def detect(
    request: DetectRequest,
    service: DetectionService = Depends(get_detection_service),
) -> DetectResponse:
    """Trigger anomaly detection on a logs/metrics window."""
    return await service.detect(request)
