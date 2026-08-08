"""Application service — drives LangGraph pipeline end-to-end."""

from orchestrator.domain.graph import build_investigation_graph
from orchestrator.domain.state import PipelineState
from orchestrator.infrastructure.agent_clients import AgentClientRegistry
from sentinel_core.schemas.contracts import AnomalyEvent, IncidentReport


class PipelineService:
  def __init__(self, *, clients: AgentClientRegistry) -> None:
      self._graph = build_investigation_graph(clients)

  async def run(self, event: AnomalyEvent) -> IncidentReport:
      initial = PipelineState(anomaly_event=event)
      final_state = await self._graph.ainvoke(initial)
      if final_state.incident_report is None:
          raise RuntimeError("Pipeline completed without incident report")
      return final_state.incident_report
