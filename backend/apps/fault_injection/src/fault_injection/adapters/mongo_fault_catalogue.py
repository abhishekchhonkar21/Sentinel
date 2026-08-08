"""MongoDB adapter for fault_catalogue repository port."""

from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorDatabase

from sentinel_core.domain.enums import CollectionName
from sentinel_core.schemas.contracts import FaultCatalogueEntry


class MongoFaultCatalogueRepository:
    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self._collection = database[CollectionName.FAULT_CATALOGUE]

    async def get_by_fault_id(self, fault_id: str) -> FaultCatalogueEntry | None:
        doc = await self._collection.find_one({"fault_id": fault_id})
        if doc is None:
            return None
        doc.pop("_id", None)
        return FaultCatalogueEntry.model_validate(doc)

    async def list_all(self) -> list[FaultCatalogueEntry]:
        entries: list[FaultCatalogueEntry] = []
        async for doc in self._collection.find().sort("fault_id", 1):
            doc.pop("_id", None)
            entries.append(FaultCatalogueEntry.model_validate(doc))
        return entries

    async def upsert(self, entry: FaultCatalogueEntry) -> None:
        payload = entry.model_dump(mode="json")
        await self._collection.update_one(
            {"fault_id": entry.fault_id},
            {"$set": payload},
            upsert=True,
        )
