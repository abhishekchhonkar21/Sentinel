"""MongoDB implementation of AnomalyEventRepository."""

from datetime import UTC, datetime

from sentinel_core.adapters.persistence.mongo_client import get_database
from sentinel_core.domain.enums import CollectionName
from sentinel_core.ports.repositories import AnomalyEventRepository
from sentinel_core.schemas.contracts import AnomalyEvent


class MongoAnomalyEventRepository(AnomalyEventRepository):
    """Concrete repository — swap for in-memory impl in unit tests."""

    def __init__(self) -> None:
        self._collection = get_database()[CollectionName.ANOMALY_EVENTS.value]

    async def get_by_anomaly_id(self, anomaly_id: str) -> AnomalyEvent | None:
        doc = await self._collection.find_one({"anomaly_id": anomaly_id})
        return AnomalyEvent.model_validate(doc) if doc else None

    async def save(self, event: AnomalyEvent) -> AnomalyEvent:
        payload = event.model_dump(mode="json")
        payload["updated_at"] = datetime.now(UTC).isoformat()
        await self._collection.update_one(
            {"anomaly_id": event.anomaly_id},
            {"$set": payload},
            upsert=True,
        )
        return event
