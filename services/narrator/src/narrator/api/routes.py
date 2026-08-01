from pydantic import BaseModel

from fastapi import APIRouter, Depends

from narrator.api.dependencies import get_narrator_agent
from narrator.application.narrator_agent import NarratorAgent
from sentinel_core.schemas.contracts import EvidenceBundle, IncidentReport, RankedHypotheses

router = APIRouter(prefix="/api/v1", tags=["narrator"])


class NarrateRequest(BaseModel):
    ranked: RankedHypotheses
    evidence: EvidenceBundle


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "narrator"}


@router.post("/narrate", response_model=IncidentReport)
async def narrate(
    request: NarrateRequest,
    agent: NarratorAgent = Depends(get_narrator_agent),
) -> IncidentReport:
    return await agent.run(request, anomaly_id=request.ranked.anomaly_id)
