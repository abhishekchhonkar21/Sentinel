"""Domain enums — shared vocabulary across services and MongoDB documents."""

from enum import StrEnum


class SignalType(StrEnum):
    LOG_PATTERN = "log_pattern"
    METRIC_SPIKE = "metric_spike"


class AgentName(StrEnum):
    DETECTOR = "detector"
    INVESTIGATOR = "investigator"
    HYPOTHESIS_RANKER = "hypothesis_ranker"
    NARRATOR = "narrator"
    CRITIC = "critic"


class GraphBackend(StrEnum):
    NETWORKX = "networkx"
    NEO4J = "neo4j"


class CollectionName(StrEnum):
    """MongoDB collection names — keep in sync with Sentinel_Project_Plan.md Section 13."""

    FAULT_CATALOGUE = "fault_catalogue"
    DEPLOYS = "deploys"
    RAW_LOGS = "raw_logs"
    ANOMALY_EVENTS = "anomaly_events"
    EVIDENCE_BUNDLES = "evidence_bundles"
    HYPOTHESES = "hypotheses"
    INCIDENT_REPORTS = "incident_reports"
    AGENT_TRACES = "agent_traces"
    FEEDBACK = "feedback"
