"""Port interfaces (hexagonal architecture) — services depend on these, not concrete adapters."""

from abc import ABC, abstractmethod

from sentinel_core.schemas.contracts import (
    AnomalyEvent,
    EvidenceBundle,
    FaultCatalogueEntry,
    IncidentReport,
    RankedHypotheses,
)


class AnomalyEventRepository(ABC):
    @abstractmethod
    async def get_by_anomaly_id(self, anomaly_id: str) -> AnomalyEvent | None: ...

    @abstractmethod
    async def save(self, event: AnomalyEvent) -> AnomalyEvent: ...


class EvidenceBundleRepository(ABC):
    @abstractmethod
    async def get_by_anomaly_id(self, anomaly_id: str) -> EvidenceBundle | None: ...

    @abstractmethod
    async def save(self, bundle: EvidenceBundle) -> EvidenceBundle: ...


class HypothesisRepository(ABC):
    @abstractmethod
    async def save(self, ranked: RankedHypotheses) -> RankedHypotheses: ...


class IncidentReportRepository(ABC):
    @abstractmethod
    async def save(self, report: IncidentReport) -> IncidentReport: ...

    @abstractmethod
    async def find_similar(self, summary: str, *, limit: int = 5) -> list[IncidentReport]: ...


class FaultCatalogueRepository(ABC):
    @abstractmethod
    async def get_by_fault_id(self, fault_id: str) -> FaultCatalogueEntry | None: ...

    @abstractmethod
    async def list_all(self) -> list[FaultCatalogueEntry]: ...
