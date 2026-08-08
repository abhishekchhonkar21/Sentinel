"""Shared FastAPI dependency providers — wire ports to concrete adapters (DI)."""

from functools import lru_cache

from sentinel_core.adapters.graph.graph_factory import build_graph_store
from sentinel_core.adapters.llm.llm_factory import build_llm_provider
from sentinel_core.adapters.persistence.anomaly_repository import MongoAnomalyEventRepository
from sentinel_core.adapters.persistence.evidence_repository import MongoEvidenceBundleRepository
from sentinel_core.adapters.persistence.trace_writer import MongoTraceWriter
from sentinel_core.config.settings import Settings
from sentinel_core.ports.graph_store import DependencyGraphStore
from sentinel_core.ports.llm_provider import LLMProvider
from sentinel_core.ports.repositories import AnomalyEventRepository, EvidenceBundleRepository
from sentinel_core.ports.trace_writer import TraceWriter


@lru_cache
def get_settings() -> Settings:
    return Settings()


def get_anomaly_repository() -> AnomalyEventRepository:
    return MongoAnomalyEventRepository()


def get_evidence_repository() -> EvidenceBundleRepository:
    return MongoEvidenceBundleRepository()


def get_trace_writer() -> TraceWriter:
    return MongoTraceWriter()


def get_graph_store() -> DependencyGraphStore:
    return build_graph_store(get_settings())


def get_llm_provider() -> LLMProvider:
    return build_llm_provider(get_settings())
