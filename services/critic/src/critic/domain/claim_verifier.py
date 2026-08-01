from sentinel_core.ports.llm_provider import LLMProvider
from sentinel_core.schemas.contracts import CriticVerdict, EvidenceBundle, IncidentReport


class ClaimVerifier:
    def __init__(self, *, llm: LLMProvider) -> None:
        self._llm = llm

    async def verify(self, report: IncidentReport, evidence: EvidenceBundle) -> CriticVerdict:
        # TODO: entity matching first pass, then constrained LLM verification
        raise NotImplementedError("Check every report claim against evidence bundle")
