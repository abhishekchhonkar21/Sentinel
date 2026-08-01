"""NarratorAgent — extends BaseAgent; thin LLM layer for incident reports."""

from narrator.api.routes import NarrateRequest
from narrator.domain.report_generator import ReportGenerator
from sentinel_core.core.base_agent import BaseAgent
from sentinel_core.domain.enums import AgentName
from sentinel_core.ports.trace_writer import TraceWriter
from sentinel_core.schemas.contracts import IncidentReport


class NarratorAgent(BaseAgent[NarrateRequest, IncidentReport]):
    agent_name = AgentName.NARRATOR.value

    def __init__(self, *, generator: ReportGenerator, trace_writer: TraceWriter) -> None:
        super().__init__(trace_writer)
        self._generator = generator

    async def _execute(self, payload: NarrateRequest) -> IncidentReport:
        return await self._generator.generate(payload.ranked, payload.evidence)
