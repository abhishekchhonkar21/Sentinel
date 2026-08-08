"""Hypothesis scoring port — rule-based and LLM-assisted scorers implement this."""

from abc import ABC, abstractmethod

from sentinel_core.schemas.contracts import EvidenceBundle, Hypothesis


class HypothesisScorer(ABC):
    @abstractmethod
    async def score(self, bundle: EvidenceBundle) -> list[Hypothesis]:
        """Return scored hypotheses sorted by evidence_score descending."""
