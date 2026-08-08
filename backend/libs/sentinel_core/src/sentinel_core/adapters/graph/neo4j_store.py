"""Neo4j implementation of DependencyGraphStore — optional backend."""

from sentinel_core.core.exceptions import ExternalServiceError
from sentinel_core.ports.graph_store import DependencyGraphStore


class Neo4jGraphStore(DependencyGraphStore):
    """Implement Cypher queries for upstream/downstream/neighbors.

    Requires neo4j driver — enable via pip install neo4j and GRAPH_BACKEND=neo4j.
    """

    def __init__(self, uri: str, user: str, password: str) -> None:
        try:
            from neo4j import GraphDatabase
        except ImportError as exc:
            raise ExternalServiceError("neo4j", "neo4j driver not installed") from exc
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def get_upstream(self, service: str) -> list[str]:
        raise NotImplementedError("Implement Cypher: MATCH (caller)-[:DEPENDS_ON]->(s) ...")

    def get_downstream(self, service: str) -> list[str]:
        raise NotImplementedError("Implement Cypher: MATCH (s)-[:DEPENDS_ON]->(dep) ...")

    def get_neighbors(self, service: str) -> list[str]:
        return sorted(set(self.get_upstream(service) + self.get_downstream(service)))
