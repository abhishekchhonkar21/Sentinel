from pydantic import BaseModel

from fastapi import APIRouter, Depends

from critic.api.dependencies import get_critic_agent
from critic.application.critic_agent import CriticAgent
from sentinel_core.schemas.contracts import CriticVerdict, EvidenceBundle, IncidentReport

router = APIRouter(prefix="/api/v1", tags=["critic"])


class VerifyRequest(BaseModel):
    report: IncidentReport
    evidence: EvidenceBundle


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "critic"}


@router.post("/verify", response_model=CriticVerdict)
async def verify(
    request: VerifyRequest,
    agent: CriticAgent = Depends(get_critic_agent),
) -> CriticVerdict:
    return await agent.run(request, anomaly_id=request.report.anomaly_id)
