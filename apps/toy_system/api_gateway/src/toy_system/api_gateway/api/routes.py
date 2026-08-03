"""HTTP routes — thin reverse proxy to downstream services."""

from typing import Annotated

from fastapi import APIRouter, Depends

from toy_system.api_gateway.api.dependencies import get_gateway_service
from toy_system.api_gateway.application.gateway_service import GatewayService
from toy_system.common.schemas import CreateOrderRequest, CreateOrderResponse

router = APIRouter(prefix="/api/v1", tags=["gateway"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "api-gateway"}


@router.post("/orders", response_model=CreateOrderResponse, status_code=201)
async def create_order(
    request: CreateOrderRequest,
    gateway: Annotated[GatewayService, Depends(get_gateway_service)],
) -> CreateOrderResponse:
    """Public entry point — forwards to orders-service."""
    return await gateway.forward_create_order(request)
