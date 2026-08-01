"""Optional LLM scorer — constrained structured output only when rules plateau."""

from sentinel_core.ports.hypothesis_scorer import HypothesisScorer
from sentinel_core.ports.llm_provider import LLMProvider
from sentinel_core.schemas.contracts import EvidenceBundle, Hypothesis


class LLMAssistedHypothesisScorer(HypothesisScorer):
    def __init__(self, llm: LLMProvider) -> None:
        self._llm = llm

    async def score(self, bundle: EvidenceBundle) -> list[Hypothesis]:
        raise NotImplementedError("Constrained JSON scoring via LLMProvider")
