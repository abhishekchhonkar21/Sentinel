"""Rule-based scorer — Week 7 default before optional LLM-assisted scorer."""

from sentinel_core.ports.hypothesis_scorer import HypothesisScorer
from sentinel_core.schemas.contracts import EvidenceBundle, Hypothesis


class RuleBasedHypothesisScorer(HypothesisScorer):
    async def score(self, bundle: EvidenceBundle) -> list[Hypothesis]:
        # TODO: weight recent deploy, dependency timing, past incident similarity
        return []
