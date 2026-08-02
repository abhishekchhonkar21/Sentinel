from pydantic import BaseModel

from sentinel_core.schemas.contracts import CriticVerdict, EvidenceBundle, IncidentReport


class VerifyRequest(BaseModel):
    report: IncidentReport
    evidence: EvidenceBundle
