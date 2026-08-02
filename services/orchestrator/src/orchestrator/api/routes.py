from fastapi import APIRouter, Depends

from orchestrator.api.dependencies import get_pipeline_service
from orchestrator.application.pipeline_service import PipelineService
from sentinel_core.schemas.contracts import AnomalyEvent, IncidentReport

router = APIRouter(prefix="/api/v1", tags=["orchestrator"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "orchestrator"}


@router.post("/investigate-incident", response_model=IncidentReport)
async def investigate_incident(
    event: AnomalyEvent,
    pipeline: PipelineService = Depends(get_pipeline_service),
) -> IncidentReport:
    return await pipeline.run(event)
