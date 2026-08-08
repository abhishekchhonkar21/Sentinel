"""Pipeline state — TypedDict / Pydantic model passed between LangGraph nodes."""

from sentinel_core.schemas.contracts import (
    AnomalyEvent,
    CriticVerdict,
    EvidenceBundle,
    IncidentReport,
    RankedHypotheses,
)


class PipelineState:
    """Mutable state bag for the investigation pipeline."""

    def __init__(self, *, anomaly_event: AnomalyEvent) -> None:
        self.anomaly_event = anomaly_event
        self.evidence_bundle: EvidenceBundle | None = None
        self.ranked_hypotheses: RankedHypotheses | None = None
        self.incident_report: IncidentReport | None = None
        self.critic_verdict: CriticVerdict | None = None
