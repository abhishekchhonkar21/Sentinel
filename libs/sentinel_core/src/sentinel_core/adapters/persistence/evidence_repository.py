"""MongoDB implementation of EvidenceBundleRepository."""

from datetime import UTC, datetime

from sentinel_core.adapters.persistence.mongo_client import get_database
from sentinel_core.domain.enums import CollectionName
from sentinel_core.ports.repositories import EvidenceBundleRepository
from sentinel_core.schemas.contracts import EvidenceBundle


class MongoEvidenceBundleRepository(EvidenceBundleRepository):
    def __init__(self) -> None:
        self._collection = get_database()[CollectionName.EVIDENCE_BUNDLES.value]

    async def get_by_anomaly_id(self, anomaly_id: str) -> EvidenceBundle | None:
        doc = await self._collection.find_one({"anomaly_id": anomaly_id})
        return EvidenceBundle.model_validate(doc) if doc else None

    async def save(self, bundle: EvidenceBundle) -> EvidenceBundle:
        payload = bundle.model_dump(mode="json")
        payload["updated_at"] = datetime.now(UTC).isoformat()
        await self._collection.update_one(
            {"anomaly_id": bundle.anomaly_id},
            {"$set": payload},
            upsert=True,
        )
        return bundle
