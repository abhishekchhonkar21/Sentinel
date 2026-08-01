"""Factory — selects graph backend from settings (Strategy + Factory patterns)."""

from sentinel_core.adapters.graph.networkx_store import NetworkXGraphStore
from sentinel_core.adapters.graph.neo4j_store import Neo4jGraphStore
from sentinel_core.config.settings import Settings
from sentinel_core.domain.enums import GraphBackend
from sentinel_core.ports.graph_store import DependencyGraphStore


def build_graph_store(settings: Settings | None = None) -> DependencyGraphStore:
    settings = settings or Settings()
    if settings.graph_backend == GraphBackend.NEO4J.value:
        return Neo4jGraphStore(settings.neo4j_uri, settings.neo4j_user, settings.neo4j_password)
    return NetworkXGraphStore()
