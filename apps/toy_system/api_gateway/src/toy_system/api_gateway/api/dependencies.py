"""Dependency injection for api-gateway."""

from functools import lru_cache

from toy_system.api_gateway.application.gateway_service import GatewayService
from toy_system.api_gateway.infrastructure.container import get_orders_client
from toy_system.api_gateway.infrastructure.settings import get_settings


@lru_cache
def get_gateway_service() -> GatewayService:
    return GatewayService(orders_client=get_orders_client(), settings=get_settings())
