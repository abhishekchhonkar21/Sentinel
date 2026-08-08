"""Pydantic DTOs — agent communication contracts (Section 6 of the plan)."""

from datetime import datetime

from pydantic import BaseModel, Field

from sentinel_core.domain.enums import SignalType


class AnomalyEvent(BaseModel):
    """Detector → Investigator (anomaly_events collection)."""

    anomaly_id: str
    service: str
    signal_type: SignalType
    confidence: float = Field(ge=0.0, le=1.0)
    detected_at: datetime
    raw_evidence_ref: str


class DeployRecord(BaseModel):
    service: str
    deployed_at: datetime
    diff_summary: str
    commit_hash: str


class PastIncidentMatch(BaseModel):
    incident_id: str
    similarity: float = Field(ge=0.0, le=1.0)


class EvidenceBundle(BaseModel):
    """Investigator → Hypothesis-Ranker (evidence_bundles collection)."""

    anomaly_id: str
    affected_service: str
    dependency_context: list[str]
    recent_deploys: list[DeployRecord]
    related_past_incidents: list[PastIncidentMatch]
    correlated_logs: list[str]
    correlated_metrics: dict[str, list[float]]


class Hypothesis(BaseModel):
    cause: str
    evidence_score: float = Field(ge=0.0, le=1.0)
    supporting_evidence: list[str]


class RankedHypotheses(BaseModel):
    """Hypothesis-Ranker → Narrator (hypotheses collection)."""

    anomaly_id: str
    hypotheses: list[Hypothesis]


class IncidentReport(BaseModel):
    """Narrator output (incident_reports collection)."""

    anomaly_id: str
    summary: str
    top_cause: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_trail: list[str]
    suggested_next_action: str


class AgentTrace(BaseModel):
    """Observability document (agent_traces collection)."""

    anomaly_id: str
    agent_name: str
    input: dict
    output: dict | None
    timestamp: datetime
    latency_ms: float
    token_usage: int | None = None


class FaultCatalogueEntry(BaseModel):
    """Ground-truth eval definition (fault_catalogue collection)."""

    fault_id: str
    description: str
    injected_service: str
    true_root_cause: str
    expected_signal_type: SignalType


class CriticVerdict(BaseModel):
    """Critic agent output."""

    grounded: bool
    flagged_claims: list[str]
