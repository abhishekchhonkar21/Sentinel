"""Application layer — request routing to downstream services."""

from toy_system.api_gateway.infrastructure.orders_client import OrdersClient
from toy_system.common.config import ToyServiceSettings
from toy_system.common.logging import configure_logging
from toy_system.common.schemas import CreateOrderRequest, CreateOrderResponse

logger = configure_logging("api-gateway")


class GatewayService:
    """API Gateway pattern — validates and forwards requests to the appropriate service.

    Week 1: only routes order creation to orders-service.
    Week 2: rate limiting and fault injection hooks will live here.
    """

    def __init__(self, *, orders_client: OrdersClient, settings: ToyServiceSettings) -> None:
        self._orders = orders_client
        self._settings = settings

    async def forward_create_order(self, request: CreateOrderRequest) -> CreateOrderResponse:
        logger.info("forwarding_order customer_id=%s items=%s", request.customer_id, len(request.items))
        return await self._orders.create_order(request)
