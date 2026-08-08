"""InvestigatorAgent — extends BaseAgent[AnomalyEvent, EvidenceBundle]."""

from investigator.domain.evidence_assembler import EvidenceAssembler
from sentinel_core.core.base_agent import BaseAgent
from sentinel_core.domain.enums import AgentName
from sentinel_core.ports.graph_store import DependencyGraphStore
from sentinel_core.ports.repositories import EvidenceBundleRepository
from sentinel_core.ports.trace_writer import TraceWriter
from sentinel_core.schemas.contracts import AnomalyEvent, EvidenceBundle


class InvestigatorAgent(BaseAgent[AnomalyEvent, EvidenceBundle]):
    agent_name = AgentName.INVESTIGATOR.value

    def __init__(
        self,
        *,
        graph_store: DependencyGraphStore,
        evidence_repo: EvidenceBundleRepository,
        trace_writer: TraceWriter,
    ) -> None:
        super().__init__(trace_writer)
        self._assembler = EvidenceAssembler(graph_store=graph_store)
        self._evidence_repo = evidence_repo

    async def _execute(self, payload: AnomalyEvent) -> EvidenceBundle:
        return await self._assembler.assemble(payload)

    async def _after_execute(
        self, payload: AnomalyEvent, result: EvidenceBundle, *, anomaly_id: str
    ) -> None:
        await self._evidence_repo.save(result)
