"""HTTP routes for inventory operations."""

from fastapi import APIRouter, Depends

from toy_system.common.schemas import InventoryItem, ReserveStockRequest, ReserveStockResponse
from toy_system.inventory_service.api.dependencies import get_inventory_service
from toy_system.inventory_service.application.inventory_service import InventoryService

router = APIRouter(prefix="/api/v1", tags=["inventory"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "inventory-service"}


@router.get("/inventory/{sku}", response_model=InventoryItem)
async def get_item(
    sku: str,
    service: InventoryService = Depends(get_inventory_service),
) -> InventoryItem:
    return await service.get_item(sku)


@router.post("/inventory/reserve", response_model=ReserveStockResponse)
async def reserve_stock(
    request: ReserveStockRequest,
    service: InventoryService = Depends(get_inventory_service),
) -> ReserveStockResponse:
    """Atomically decrement stock for an order — fails with 409 if insufficient."""
    return await service.reserve_stock(request)
