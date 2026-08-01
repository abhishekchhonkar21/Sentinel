"""Dependency graph port — NetworkX and Neo4j adapters implement this interface."""

from abc import ABC, abstractmethod


class DependencyGraphStore(ABC):
    @abstractmethod
    def get_upstream(self, service: str) -> list[str]:
        """Services that call *service* (dependents)."""

    @abstractmethod
    def get_downstream(self, service: str) -> list[str]:
        """Services *service* depends on."""

    @abstractmethod
    def get_neighbors(self, service: str) -> list[str]:
        """Full immediate dependency context for investigator evidence bundles."""
