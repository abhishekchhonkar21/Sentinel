"""Domain service — pure evidence assembly logic, no HTTP or MongoDB imports."""

from sentinel_core.ports.graph_store import DependencyGraphStore
from sentinel_core.schemas.contracts import AnomalyEvent, EvidenceBundle


class EvidenceAssembler:
    """Queries dependency graph, deploys, logs/metrics — returns EvidenceBundle."""

    def __init__(self, *, graph_store: DependencyGraphStore) -> None:
        self._graph = graph_store

    async def assemble(self, event: AnomalyEvent) -> EvidenceBundle:
        # TODO: query deploys collection, raw_logs time window, past incidents
        return EvidenceBundle(
            anomaly_id=event.anomaly_id,
            affected_service=event.service,
            dependency_context=self._graph.get_neighbors(event.service),
            recent_deploys=[],
            related_past_incidents=[],
            correlated_logs=[],
            correlated_metrics={},
        )
