"""Application layer — inventory use cases."""

from toy_system.common.config import ToyServiceSettings
from toy_system.common.logging import configure_logging
from toy_system.common.schemas import InventoryItem, ReserveStockRequest, ReserveStockResponse
from toy_system.inventory_service.domain.exceptions import InsufficientStockError, ItemNotFoundError
from toy_system.inventory_service.ports.inventory_repository import InventoryRepository

logger = configure_logging("inventory-service")


class InventoryService:
    """Orchestrates stock reads and atomic reservations against MongoDB."""

    def __init__(self, *, repository: InventoryRepository, settings: ToyServiceSettings) -> None:
        self._repo = repository
        self._settings = settings

    async def get_item(self, sku: str) -> InventoryItem:
        item = await self._repo.find_by_sku(sku)
        if item is None:
            raise ItemNotFoundError(sku)
        return item

    async def reserve_stock(self, request: ReserveStockRequest) -> ReserveStockResponse:
        logger.info(
            "reserving_stock order_id=%s sku=%s qty=%s",
            request.order_id,
            request.sku,
            request.quantity,
        )
        try:
            remaining = await self._repo.reserve_atomic(
                sku=request.sku,
                quantity=request.quantity,
            )
        except InsufficientStockError:
            logger.warning(
                "insufficient_stock order_id=%s sku=%s qty=%s",
                request.order_id,
                request.sku,
                request.quantity,
            )
            raise

        return ReserveStockResponse(
            order_id=request.order_id,
            sku=request.sku,
            reserved=request.quantity,
            remaining=remaining,
        )
