from pydantic import BaseModel

from sentinel_core.schemas.contracts import EvidenceBundle, RankedHypotheses


class NarrateRequest(BaseModel):
    ranked: RankedHypotheses
    evidence: EvidenceBundle
