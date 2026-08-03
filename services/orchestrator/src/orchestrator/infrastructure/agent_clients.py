"""HTTP client adapters — orchestrator calls agent services via these ports."""

from abc import ABC, abstractmethod

import httpx

from sentinel_core.config.settings import Settings
from sentinel_core.schemas.contracts import (
    AnomalyEvent,
    CriticVerdict,
    EvidenceBundle,
    IncidentReport,
    RankedHypotheses,
)


class InvestigatorClient(ABC):
    @abstractmethod
    async def investigate(self, event: AnomalyEvent) -> EvidenceBundle: ...


class RankerClient(ABC):
    @abstractmethod
    async def rank(self, bundle: EvidenceBundle) -> RankedHypotheses: ...


class NarratorClient(ABC):
    @abstractmethod
    async def narrate(
        self, ranked: RankedHypotheses, evidence: EvidenceBundle
    ) -> IncidentReport: ...


class CriticClient(ABC):
    @abstractmethod
    async def verify(
        self, report: IncidentReport, evidence: EvidenceBundle
    ) -> CriticVerdict: ...


class AgentClientRegistry:
    investigator: InvestigatorClient
    ranker: RankerClient
    narrator: NarratorClient
    critic: CriticClient


class HttpInvestigatorClient(InvestigatorClient):
    def __init__(self, base_url: str) -> None:
        self._base_url = base_url.rstrip("/")

    async def investigate(self, event: AnomalyEvent) -> EvidenceBundle:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self._base_url}/api/v1/investigate",
                json=event.model_dump(mode="json"),
            )
            resp.raise_for_status()
            return EvidenceBundle.model_validate(resp.json())


class HttpRankerClient(RankerClient):
    def __init__(self, base_url: str) -> None:
        self._base_url = base_url.rstrip("/")

    async def rank(self, bundle: EvidenceBundle) -> RankedHypotheses:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self._base_url}/api/v1/rank",
                json=bundle.model_dump(mode="json"),
            )
            resp.raise_for_status()
            return RankedHypotheses.model_validate(resp.json())


class HttpNarratorClient(NarratorClient):
    def __init__(self, base_url: str) -> None:
        self._base_url = base_url.rstrip("/")

    async def narrate(
        self, ranked: RankedHypotheses, evidence: EvidenceBundle
    ) -> IncidentReport:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self._base_url}/api/v1/narrate",
                json={
                    "ranked": ranked.model_dump(mode="json"),
                    "evidence": evidence.model_dump(mode="json"),
                },
            )
            resp.raise_for_status()
            return IncidentReport.model_validate(resp.json())


class HttpCriticClient(CriticClient):
    def __init__(self, base_url: str) -> None:
        self._base_url = base_url.rstrip("/")

    async def verify(
        self, report: IncidentReport, evidence: EvidenceBundle
    ) -> CriticVerdict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self._base_url}/api/v1/verify",
                json={
                    "report": report.model_dump(mode="json"),
                    "evidence": evidence.model_dump(mode="json"),
                },
            )
            resp.raise_for_status()
            return CriticVerdict.model_validate(resp.json())


class HttpAgentClientRegistry(AgentClientRegistry):
    def __init__(self, settings: Settings | None = None) -> None:
        settings = settings or Settings()
        self.investigator = HttpInvestigatorClient(settings.investigator_url)
        self.ranker = HttpRankerClient(settings.hypothesis_ranker_url)
        self.narrator = HttpNarratorClient(settings.narrator_url)
        self.critic = HttpCriticClient(settings.critic_url)
