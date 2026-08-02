"""HTTP routes for order placement."""

from fastapi import APIRouter, Depends

from toy_system.common.schemas import CreateOrderRequest, CreateOrderResponse
from toy_system.orders_service.api.dependencies import get_order_service
from toy_system.orders_service.application.order_service import OrderService

router = APIRouter(prefix="/api/v1", tags=["orders"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "orders-service"}


@router.post("/orders", response_model=CreateOrderResponse, status_code=201)
async def create_order(
    request: CreateOrderRequest,
    service: OrderService = Depends(get_order_service),
) -> CreateOrderResponse:
    """Place an order: reserve stock → charge payment → confirm."""
    return await service.place_order(request)
