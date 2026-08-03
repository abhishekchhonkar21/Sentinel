from critic.domain.claim_verifier import ClaimVerifier
from critic.domain.models import VerifyRequest
from sentinel_core.core.base_agent import BaseAgent
from sentinel_core.domain.enums import AgentName
from sentinel_core.ports.trace_writer import TraceWriter
from sentinel_core.schemas.contracts import CriticVerdict


class CriticAgent(BaseAgent[VerifyRequest, CriticVerdict]):
    agent_name = AgentName.CRITIC.value

    def __init__(self, *, verifier: ClaimVerifier, trace_writer: TraceWriter) -> None:
        super().__init__(trace_writer)
        self._verifier = verifier

    async def _execute(self, payload: VerifyRequest) -> CriticVerdict:
        return await self._verifier.verify(payload.report, payload.evidence)
