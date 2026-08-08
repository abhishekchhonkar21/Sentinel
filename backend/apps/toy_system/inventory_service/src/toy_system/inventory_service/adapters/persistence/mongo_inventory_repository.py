"""MongoDB repository — atomic findOneAndUpdate for stock reservations."""

from __future__ import annotations

import asyncio

from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
from pymongo import ReturnDocument

from toy_system.common.fault_state import fault_state_store
from toy_system.common.schemas import InventoryItem
from toy_system.inventory_service.domain.exceptions import InsufficientStockError, ItemNotFoundError
from toy_system.inventory_service.ports.inventory_repository import InventoryRepository

COLLECTION_NAME = "inventory_items"


class MongoInventoryRepository(InventoryRepository):
    """Concrete adapter — uses MongoDB $inc with a quantity guard for atomicity.

    This is a real DB dependency that Week 2 fault injection can stress
    (e.g. connection pool exhaustion → latency spikes without hard errors).
    """

    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self._collection: AsyncIOMotorCollection = database[COLLECTION_NAME]

    async def _maybe_delay(self) -> None:
        delay_ms = fault_state_store.get().db_latency_delay_ms
        if delay_ms > 0:
            await asyncio.sleep(delay_ms / 1000)

    async def find_by_sku(self, sku: str) -> InventoryItem | None:
        await self._maybe_delay()
        doc = await self._collection.find_one({"sku": sku})
        if doc is None:
            return None
        return InventoryItem(
            sku=doc["sku"],
            name=doc["name"],
            quantity=doc["quantity"],
            price_cents=doc["price_cents"],
        )

    async def reserve_atomic(self, *, sku: str, quantity: int) -> int:
        await self._maybe_delay()
        # Only decrement if enough stock remains — prevents overselling under concurrency.
        result = await self._collection.find_one_and_update(
            {"sku": sku, "quantity": {"$gte": quantity}},
            {"$inc": {"quantity": -quantity}},
            return_document=ReturnDocument.AFTER,
        )
        if result is None:
            current = await self.find_by_sku(sku)
            if current is None:
                raise ItemNotFoundError(sku)
            raise InsufficientStockError(sku, quantity, current.quantity)
        return int(result["quantity"])

    async def seed_if_empty(self, items: list[InventoryItem]) -> None:
        count = await self._collection.count_documents({})
        if count > 0:
            return
        await self._collection.insert_many([item.model_dump() for item in items])
