"""HypothesisRankerAgent — extends BaseAgent[EvidenceBundle, RankedHypotheses]."""

from sentinel_core.core.base_agent import BaseAgent
from sentinel_core.domain.enums import AgentName
from sentinel_core.ports.hypothesis_scorer import HypothesisScorer
from sentinel_core.ports.trace_writer import TraceWriter
from sentinel_core.schemas.contracts import EvidenceBundle, RankedHypotheses


class HypothesisRankerAgent(BaseAgent[EvidenceBundle, RankedHypotheses]):
    agent_name = AgentName.HYPOTHESIS_RANKER.value

    def __init__(self, *, scorer: HypothesisScorer, trace_writer: TraceWriter) -> None:
        super().__init__(trace_writer)
        self._scorer = scorer

    async def _execute(self, payload: EvidenceBundle) -> RankedHypotheses:
        hypotheses = await self._scorer.score(payload)
        return RankedHypotheses(anomaly_id=payload.anomaly_id, hypotheses=hypotheses)
