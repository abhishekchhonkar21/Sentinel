from pydantic import BaseModel

from sentinel_core.schemas.contracts import EvidenceBundle, IncidentReport


class VerifyRequest(BaseModel):
    report: IncidentReport
    evidence: EvidenceBundle
