"""NetworkX implementation of DependencyGraphStore — default for v1."""

import networkx as nx

from sentinel_core.ports.graph_store import DependencyGraphStore


class NetworkXGraphStore(DependencyGraphStore):
    """In-memory directed graph encoding the toy microservice topology."""

    def __init__(self) -> None:
        self._graph = nx.DiGraph()
        self._seed_default_topology()

    def _seed_default_topology(self) -> None:
        """api-gateway → orders → {payments, inventory} → external-payment-mock."""
        edges = [
            ("api-gateway", "orders-service"),
            ("orders-service", "payments-service"),
            ("orders-service", "inventory-service"),
            ("payments-service", "external-payment-mock"),
        ]
        self._graph.add_edges_from(edges)

    def get_upstream(self, service: str) -> list[str]:
        return list(self._graph.predecessors(service))

    def get_downstream(self, service: str) -> list[str]:
        return list(self._graph.successors(service))

    def get_neighbors(self, service: str) -> list[str]:
        return sorted(set(self.get_upstream(service) + self.get_downstream(service)))
