"""Domain service — structured LLM prompt + schema validation."""

from sentinel_core.ports.llm_provider import LLMProvider
from sentinel_core.schemas.contracts import EvidenceBundle, IncidentReport, RankedHypotheses


class ReportGenerator:
    def __init__(self, *, llm: LLMProvider) -> None:
        self._llm = llm

    async def generate(
        self, ranked: RankedHypotheses, evidence: EvidenceBundle
    ) -> IncidentReport:
        # TODO: build constrained prompt from ranked + evidence; validate IncidentReport schema
        raise NotImplementedError("Wire LLMProvider.complete_structured with guardrails")
