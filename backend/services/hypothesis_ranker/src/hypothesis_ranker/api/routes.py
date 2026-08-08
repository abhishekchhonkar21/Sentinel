from fastapi import APIRouter, Depends

from hypothesis_ranker.api.dependencies import get_ranker_agent
from hypothesis_ranker.application.ranker_agent import HypothesisRankerAgent
from sentinel_core.schemas.contracts import EvidenceBundle, RankedHypotheses

router = APIRouter(prefix="/api/v1", tags=["hypothesis-ranker"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "hypothesis_ranker"}


@router.post("/rank", response_model=RankedHypotheses)
async def rank(
    bundle: EvidenceBundle,
    agent: HypothesisRankerAgent = Depends(get_ranker_agent),
) -> RankedHypotheses:
    return await agent.run(bundle, anomaly_id=bundle.anomaly_id)
