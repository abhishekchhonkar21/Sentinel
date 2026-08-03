"""Repository port — inventory persistence abstraction (hexagonal architecture)."""

from abc import ABC, abstractmethod

from toy_system.common.schemas import InventoryItem


class InventoryRepository(ABC):
    @abstractmethod
    async def find_by_sku(self, sku: str) -> InventoryItem | None: ...

    @abstractmethod
    async def reserve_atomic(self, *, sku: str, quantity: int) -> int:
        """Decrement stock atomically; return remaining quantity.

        Raises InsufficientStockError if stock is insufficient.
        """

    @abstractmethod
    async def seed_if_empty(self, items: list[InventoryItem]) -> None:
        """Insert default catalog only when the collection is empty (first boot)."""
