from fastapi import APIRouter, Depends

from investigator.api.dependencies import get_investigator_agent
from investigator.application.investigator_agent import InvestigatorAgent
from sentinel_core.schemas.contracts import AnomalyEvent, EvidenceBundle

router = APIRouter(prefix="/api/v1", tags=["investigator"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "investigator"}


@router.post("/investigate", response_model=EvidenceBundle)
async def investigate(
    event: AnomalyEvent,
    agent: InvestigatorAgent = Depends(get_investigator_agent),
) -> EvidenceBundle:
    return await agent.run(event, anomaly_id=event.anomaly_id)
